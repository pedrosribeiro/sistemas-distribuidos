import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router";

// Tipos para o sistema
interface Itinerario {
    id: string;
    lugares_visitados: string[];
    datas_embarque: string[];
    porto_embarque: string;
    valor_por_pessoa: number;
    cabines_disponiveis: number;
    descricao?: string;
    nome_navio?: string;
    numero_noites?: number;
}

interface ReservaForm {
    data_embarque: string;
    numero_passageiros: number;
    numero_cabines: number;
    cliente_id: string;
}

export function meta() {
    return [
        { title: "Criar Reserva - Sistema de Cruzeiros" },
        {
            name: "description",
            content: "Formulário para criar uma nova reserva de cruzeiro",
        },
    ];
}

export default function Reservar() {
    const { itinerarioId } = useParams();
    const navigate = useNavigate();

    const [itinerario, setItinerario] = useState<Itinerario | null>(null);
    const [loading, setLoading] = useState(false);
    const [loadingItinerario, setLoadingItinerario] = useState(true);
    const [error, setError] = useState<string>("");
    const [success, setSuccess] = useState<string>("");

    const [formData, setFormData] = useState<ReservaForm>({
        data_embarque: "",
        numero_passageiros: 1,
        numero_cabines: 1,
        cliente_id: "",
    });

    // Carregar dados do itinerário
    useEffect(() => {
        const carregarItinerario = async () => {
            if (!itinerarioId) {
                setError("ID do itinerário não fornecido");
                setLoadingItinerario(false);
                return;
            }

            try {
                const response = await fetch(
                    `http://localhost:5001/api/itinerarios/${itinerarioId}`,
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                            "mode": "cors"
                        },
                    }
                );

                if (!response.ok) {
                    throw new Error("Itinerário não encontrado");
                }

                const itinerarioData = await response.json();
                setItinerario(itinerarioData);
            } catch (error) {
                console.error("Erro ao carregar itinerário:", error);
                setError("Erro ao carregar dados do itinerário");
            } finally {
                setLoadingItinerario(false);
            }
        };

        carregarItinerario();
    }, [itinerarioId]);

    // Função para processar reserva
    const handleSubmitReserva = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        // Validações
        if (!formData.cliente_id) {
            setError("Nome do cliente é obrigatório");
            return;
        }

        if (!formData.data_embarque) {
            setError("Data de embarque é obrigatória");
            return;
        }

        if (formData.numero_passageiros < 1) {
            setError("Número de passageiros deve ser maior que 0");
            return;
        }

        if (formData.numero_cabines < 1 || formData.numero_cabines > itinerario?.cabines_disponiveis!) {
            setError("Número de cabines indisponivel");
            return;
        }

        if (!itinerario) {
            setError("Dados do itinerário não encontrados");
            return;
        }

        setLoading(true);
        try {
            const reservaData = {
                itinerario_id: itinerarioId,
                data_embarque: formData.data_embarque,
                numero_passageiros: formData.numero_passageiros,
                numero_cabines: formData.numero_cabines,
                cliente_id: formData.cliente_id.trim(),
                valor_por_pessoa: itinerario.valor_por_pessoa
            };

            const response = await fetch(
                "http://localhost:5001/api/reservas",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(reservaData),
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                console.log(errorData.erro)
                throw new Error(errorData.erro || "Erro ao criar reserva");
            }

            const resultado = await response.json();
            setSuccess("Reserva criada com sucesso! Redirecionando para o pagamento...");

            if (resultado && formData.cliente_id) {
                const eventSource = new EventSource(
                    `http://localhost:5001/api/sse/reserva/${encodeURIComponent(formData.cliente_id)}`
                );
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.tipo !== 'heartbeat') {
                            alert(`Notificação: ${JSON.stringify(data.mensagem)}`);
                        }
                    } catch {
                        alert(`Notificação recebida: ${event.data.mensagem}`);
                    }
                };
            }

            // Redirecionar para página de pagamento ou home após 2 segundos
            setTimeout(() => {
                if (resultado) {
                    window.open(resultado.link_pagamento, '_blank');
                }
            }, 2000);

        } catch (error) {
            console.error("Erro ao criar reserva:", error);
            setError(error instanceof Error ? error.message : "Erro ao criar reserva");
        } finally {
            setLoading(false);
        }
    };

    // Calcular valor total
    const valorTotal = itinerario
        ? itinerario.valor_por_pessoa * formData.numero_passageiros
        : 0;

    if (loadingItinerario) {
        return (
            <div className="min-h-screen bg-gray-50 py-12 px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Carregando dados do itinerário...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error && !itinerario) {
        return (
            <div className="min-h-screen bg-gray-50 py-12 px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-white rounded-lg shadow-lg p-6">
                        <div className="text-center">
                            <h1 className="text-2xl font-bold text-red-600 mb-4">Erro</h1>
                            <p className="text-gray-600 mb-6">{error}</p>
                            <Link
                                to="/"
                                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200"
                            >
                                ← Voltar à página inicial
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Criar Reserva
                    </h1>
                    <p className="text-xl text-gray-600">
                        Complete os dados abaixo para finalizar sua reserva
                    </p>
                </div>

                {/* Informações do Itinerário */}
                {itinerario && (
                    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h2 className="text-2xl font-semibold mb-4 text-black">
                            Dados do Cruzeiro
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 className="text-lg font-bold text-gray-900 mb-2">
                                    {itinerario.lugares_visitados[itinerario.lugares_visitados.length - 1]}
                                </h3>
                                <p className="text-gray-600 mb-2">{itinerario.descricao}</p>
                                <div className="space-y-1">
                                    <p className="text-sm text-gray-500">
                                        <span className="font-medium">Porto de Embarque:</span> {itinerario.porto_embarque}
                                    </p>
                                    {itinerario.nome_navio && (
                                        <p className="text-sm text-gray-500">
                                            <span className="font-medium">Navio:</span> {itinerario.nome_navio}
                                        </p>
                                    )}
                                    {itinerario.numero_noites && (
                                        <p className="text-sm text-gray-500">
                                            <span className="font-medium">Duração:</span> {itinerario.numero_noites} noites
                                        </p>
                                    )}
                                </div>
                            </div>
                            <div>
                                <h4 className="font-medium text-gray-700 mb-2">Lugares Visitados:</h4>
                                <ul className="text-sm text-gray-600 space-y-1">
                                    {itinerario.lugares_visitados.map((lugar, index) => (
                                        <li key={index} className="flex items-center">
                                            <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                                            {lugar}
                                        </li>
                                    ))}
                                </ul>
                                <div className="mt-4 p-3 bg-green-50 rounded-md">
                                    <p className="text-lg font-bold text-green-800">
                                        R$ {itinerario.valor_por_pessoa.toLocaleString("pt-BR")}
                                        <span className="text-sm font-normal text-green-600"> por pessoa</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Formulário de Reserva */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h2 className="text-2xl font-semibold mb-6 text-black">
                        Dados da Reserva
                    </h2>

                    {error && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-red-800">{error}</p>
                        </div>
                    )}

                    {success && (
                        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
                            <p className="text-green-800">{success}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmitReserva} className="space-y-6">
                        {/* Nome do Cliente */}
                        <div>
                            <label
                                htmlFor="cliente"
                                className="block text-sm font-medium text-gray-700 mb-2"
                            >
                                Nome Completo *
                            </label>
                            <input
                                type="text"
                                id="cliente_id"
                                required
                                value={formData.cliente_id}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        cliente_id: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-400"
                                placeholder="Digite seu nome completo"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Data de Embarque */}
                            <div>
                                <label
                                    htmlFor="data_embarque"
                                    className="block text-sm font-medium text-gray-700 mb-2"
                                >
                                    Data de Embarque *
                                </label>
                                <select
                                    id="data_embarque"
                                    required
                                    value={formData.data_embarque}
                                    onChange={(e) =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            data_embarque: e.target.value,
                                        }))
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                                >
                                    <option value="">Selecione uma data</option>
                                    {itinerario?.datas_embarque.map((data) => (
                                        <option key={data} value={data}>
                                            {new Date(data + 'T00:00:00').toLocaleDateString("pt-BR")}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Número de Passageiros */}
                            <div>
                                <label
                                    htmlFor="numero_passageiros"
                                    className="block text-sm font-medium text-gray-700 mb-2"
                                >
                                    Número de Passageiros *
                                </label>
                                <input
                                    type="number"
                                    id="numero_passageiros"
                                    min="1"
                                    max="10"
                                    required
                                    value={formData.numero_passageiros}
                                    onChange={(e) =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            numero_passageiros: parseInt(e.target.value) || 1,
                                        }))
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                                />
                            </div>

                            {/* Número de Cabines */}
                            <div>
                                <label
                                    htmlFor="numero_cabines"
                                    className="block text-sm font-medium text-gray-700 mb-2"
                                >
                                    Número de Cabines *
                                </label>
                                <input
                                    type="number"
                                    id="numero_cabines"
                                    min="1"
                                    max="5"
                                    required
                                    value={formData.numero_cabines}
                                    onChange={(e) =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            numero_cabines: parseInt(e.target.value) || 1,
                                        }))
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                                />
                            </div>
                        </div>

                        {/* Resumo do Valor */}
                        {itinerario && (
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                                    Resumo da Reserva
                                </h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Valor por pessoa:</span>
                                        <span className="text-gray-900">
                                            R$ {itinerario.valor_por_pessoa.toLocaleString("pt-BR")}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Número de passageiros:</span>
                                        <span className="text-gray-900">{formData.numero_passageiros}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Número de cabines:</span>
                                        <span className="text-gray-900">{formData.numero_cabines}</span>
                                    </div>
                                    <div className="border-t pt-2">
                                        <div className="flex justify-between text-lg font-bold">
                                            <span className="text-gray-900">Total:</span>
                                            <span className="text-green-600">
                                                R$ {valorTotal.toLocaleString("pt-BR")}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Botões de Ação */}
                        <div className="flex space-x-4">
                            <Link
                                to="/"
                                className="flex-1 bg-gray-600 text-white py-3 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors text-center"
                            >
                                ← Voltar
                            </Link>
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex-1 bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            >
                                {loading ? (
                                    <>
                                        <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                                        Processando...
                                    </>
                                ) : (
                                    "Confirmar Reserva"
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
