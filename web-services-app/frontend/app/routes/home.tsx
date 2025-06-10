import { useState, useEffect } from "react";
import { Link } from "react-router";

// Tipos para o sistema
interface Itinerario {
    id: string;
    lugares_visitados: string[];
    datas_embarque: string[];
    porto_embarque: string;
    valor_por_pessoa: number;
    descricao?: string;
}

interface Reserva {
    id: string;
    itinerario_id: string;
    data_embarque: string;
    cliente: string;
    num_passageiros: number;
    valor_por_pessoa: number;
    num_cabines: number;
    valor_total: number;
    data_criacao: string;
}

interface FiltroItinerarios {
    destino: string;
    data_embarque: string;
    porto_embarque: string;
}

export function meta() {
    return [
        { title: "Sistema de Reservas - Cruzeiros" },
        {
            name: "description",
            content: "Sistema de reservas para cruzeiros marítimos",
        },
    ];
}

export default function Home() {
    const [itinerarios, setItinerarios] = useState<Itinerario[]>([]);
    const [loading, setLoading] = useState(false);
    const [filtros, setFiltros] = useState<FiltroItinerarios>({
        destino: "",
        data_embarque: "",
        porto_embarque: "",
    });

    const consultarItinerarios = async (
        filtros?: Partial<FiltroItinerarios>
    ) => {
        const params = new URLSearchParams();

        if (filtros?.destino) params.set("destino", filtros.destino);
        if (filtros?.data_embarque)
            params.set("data_embarque", filtros.data_embarque);
        if (filtros?.porto_embarque)
            params.set("porto_embarque", filtros.porto_embarque);

        const response = await fetch(
            `http://localhost:5001/api/itinerarios?${params.toString()}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "mode": "cors"
                },
            }

        );

        const itinerarios = await response.json();

        setItinerarios(itinerarios);
    };

    // Carrega itinerários iniciais
    useEffect(() => {
        const carregarItinerarios = async () => {
            setLoading(true);
            try {
                await consultarItinerarios();
            } catch (error) {
                console.error("Erro ao carregar itinerários:", error);
            } finally {
                setLoading(false);
            }
        };

        carregarItinerarios();
    }, []);

    // Função para filtrar itinerários
    const handleFiltrarItinerarios = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await consultarItinerarios(filtros);
        } catch (error) {
            console.error("Erro ao filtrar itinerários:", error);
        } finally {
            setLoading(false);
        }
    };

    // Função para processar reserva
    const handleReservar = async (e: React.FormEvent) => {
        e.preventDefault();

        const formData = new FormData(e.target as HTMLFormElement);
        const cliente = formData.get("cliente") as string;
        const num_passageiros = parseInt(
            formData.get("num_passageiros") as string
        );
        const num_cabines = parseInt(formData.get("num_cabines") as string);
        const data_embarque = formData.get("data_embarque") as string;

        setLoading(true);
        try {
        } catch (error) {
            console.error("Erro ao criar reserva:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Sistema de Reservas de Cruzeiros
                    </h1>
                    <p className="text-xl text-gray-600">
                        Encontre e reserve o cruzeiro dos seus sonhos
                    </p>

                    {/* Menu de Navegação */}
                    <div className="mt-8 flex justify-center space-x-4">
                        <Link
                            to="/status"
                            className="inline-flex items-center px-6 py-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition duration-200"
                        >
                            📊 Ver Status das Reservas
                        </Link>
                    </div>
                </div>

                {/* Formulário de Filtros */}
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-semibold mb-6 text-black">
                        Buscar Itinerários
                    </h2>
                    <form
                        onSubmit={handleFiltrarItinerarios}
                        className="grid grid-cols-1 md:grid-cols-4 gap-4"
                    >
                        <div>
                            <label
                                htmlFor="destino"
                                className="block text-sm font-medium text-gray-700 mb-2"
                            >
                                Destino
                            </label>
                            <input
                                type="text"
                                id="destino"
                                value={filtros.destino}
                                onChange={(e) =>
                                    setFiltros((prev) => ({
                                        ...prev,
                                        destino: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-400"
                                placeholder="Ex: Caribe"
                            />
                        </div>
                        <div>
                            <label
                                htmlFor="data_embarque"
                                className="block text-sm font-medium text-gray-700 mb-2"
                            >
                                Data de Embarque
                            </label>
                            <input
                                type="date"
                                id="data_embarque"
                                value={filtros.data_embarque}
                                onChange={(e) =>
                                    setFiltros((prev) => ({
                                        ...prev,
                                        data_embarque: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                            />
                        </div>
                        <div>
                            <label
                                htmlFor="porto_embarque"
                                className="block text-sm font-medium text-gray-700 mb-2"
                            >
                                Porto de Embarque
                            </label>
                            <select
                                id="porto_embarque"
                                value={filtros.porto_embarque}
                                onChange={(e) =>
                                    setFiltros((prev) => ({
                                        ...prev,
                                        porto_embarque: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                            >
                                <option value="">Todos os portos</option>
                                <option value="Santos">Santos</option>
                                <option value="Rio de Janeiro">
                                    Rio de Janeiro
                                </option>
                            </select>
                        </div>
                        <div className="flex items-end">
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
                            >
                                {loading ? "Buscando..." : "Buscar"}
                            </button>
                        </div>
                    </form>
                </div>

                {/* Lista de Itinerários */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {itinerarios.map((itinerario) => (
                        <div
                            key={itinerario.id}
                            className="bg-white rounded-lg shadow-lg overflow-hidden"
                        >
                            <div className="p-6 h-full flex flex-col justify-between">
                                <h3 className="text-xl font-bold text-gray-900 mb-2">
                                    {itinerario.lugares_visitados[itinerario.lugares_visitados.length - 1]}
                                </h3>
                                <p className="text-gray-600 mb-4">
                                    {itinerario.descricao}
                                </p>
                                <h3 className="text-sm font-bold text-gray-600">Lugares Visitados</h3>
                                <ul className="text-gray-500 text-sm mb-4">
                                    {itinerario.lugares_visitados.map((lugar: string, index: number) => (
                                        <li key={lugar}>{lugar}</li>
                                    ))}
                                </ul>

                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium text-gray-500">
                                            Porto de Embarque:
                                        </span>
                                        <span className="text-sm text-gray-900">
                                            {itinerario.porto_embarque}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium text-gray-500">
                                            Datas Disponíveis:
                                        </span>
                                        <span className="text-sm text-gray-900">
                                            {itinerario.datas_embarque.length}{" "}
                                            opções
                                        </span>
                                    </div>
                                </div>

                                <div className="border-t pt-4">
                                    <div className="flex justify-between items-center mb-4">
                                        <span className="text-lg font-bold text-gray-900">
                                            R${" "}
                                            {itinerario.valor_por_pessoa.toLocaleString(
                                                "pt-BR"
                                            )}
                                        </span>
                                        <span className="text-sm text-gray-500">
                                            por pessoa
                                        </span>
                                    </div>

                                    <Link
                                        to={`/reservar/${itinerario.id}`}
                                        className="w-full"
                                    >
                                        <button className="cursor-pointer w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors">
                                            Reservar Agora
                                        </button>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {itinerarios.length === 0 && !loading && (
                    <div className="text-center py-12">
                        <p className="text-xl text-gray-500">
                            Nenhum itinerário encontrado com os filtros
                            selecionados.
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}
