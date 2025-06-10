import { useState, useEffect, useRef } from "react";
import { createCookie, Link } from "react-router";

// Tipos para o sistema
interface Itinerario {
    id: string;
    lugares_visitados: string[];
    datas_embarque: string[];
    cabines_disponiveis: number;
    porto_embarque: string;
    valor_por_pessoa: number;
    descricao?: string;
}

interface Reserva {
    id: string;
    itinerario_id: string;
    data_embarque: string;
    cliente: string;
    numero_passageiros: number;
    valor_por_pessoa: number;
    numero_cabines: number;
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

function setCookie(name: string, value: string, days = 30) {
    if (typeof document === "undefined") return;
    const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
}

function getCookie(name: string) {
    if (typeof document === "undefined") return "";
    const value = document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1];
    return value ? decodeURIComponent(value) : "";
}

function deleteCookie(name: string) {
    if (typeof document === "undefined") return;
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

export default function Home() {
    const [itinerarios, setItinerarios] = useState<Itinerario[]>([]);
    const [loading, setLoading] = useState(false);
    const [notificacoes, setNotificacoes] = useState<string[]>([]);
    const [clienteId, setClienteId] = useState<string>("");
    const [filtros, setFiltros] = useState<FiltroItinerarios>({
        destino: "",
        data_embarque: "",
        porto_embarque: "",
    });
    const [isSubscribed, setIsSubscribed] = useState<boolean>(false);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Inicializar clienteId do cookie ao carregar a página
    useEffect(() => {
        const savedClienteId = getCookie("clienteId");
        if (savedClienteId) {
            setClienteId(savedClienteId);
            setIsSubscribed(true);
            // Conectar automaticamente ao SSE se já houver um clienteId salvo
            conectarSSE(savedClienteId);
        }
    }, []);

    // Função para conectar ao SSE
    const conectarSSE = (cliente: string) => {
        // Fechar conexão anterior se existir
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        const eventSource = new EventSource(
            `http://localhost:5001/api/sse/promocoes/${encodeURIComponent(cliente)}`
        );
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.tipo !== 'heartbeat') {
                    setNotificacoes(prev => [...prev, `Promoção: ${JSON.stringify(data.mensagem)}`]);
                }
            } catch {
                setNotificacoes(prev => [...prev, `Promoção: ${event.data}`]);
            }
        };

        eventSource.onerror = (error) => {
            console.error("Erro na conexão SSE:", error);
        };

        eventSourceRef.current = eventSource;
    };

    // Função para desconectar do SSE
    const desconectarSSE = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
    };

    // Limpar conexão SSE ao desmontar o componente
    useEffect(() => {
        return () => {
            desconectarSSE();
        };
    }, []);

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

    const handlePromocao = async () => {
        if (clienteId) {
            try {
                // Salvar clienteId no cookie
                setCookie("clienteId", clienteId);
                setIsSubscribed(true);

                // Conectar ao SSE
                conectarSSE(clienteId);
                
                setNotificacoes(prev => [...prev, `Você está inscrito para receber promoções!`]);
            } catch (error) {
                console.error("Erro ao registrar interesse em promoções:", error);
                setNotificacoes(prev => [...prev, `Erro ao registrar interesse em promoções`]);
            }
        }
    }

    const handleCancelarPromocao = async () => {
        if (clienteId) {
            try {
                // Cancelar interesse em promoções via API
                const eventSource = new EventSource(
                    `http://localhost:5001/api/sse/cancelar_promocoes/${encodeURIComponent(clienteId)}`
                );
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.tipo !== 'heartbeat') {
                            setNotificacoes(prev => [...prev, `Notificação: ${JSON.stringify(data.mensagem)}`]);
                        }
                    } catch {
                        setNotificacoes(prev => [...prev, `Notificação: ${event.data.mensagem}`]);
                    }
                };
                
                // Remover cookie
                deleteCookie("clienteId");
                
                // Resetar estados
                setIsSubscribed(false);
                setClienteId("");
                
                setNotificacoes(prev => [...prev, `Notificações de promoção desativadas!`]);
            } catch (error) {
                console.error("Erro ao cancelar interesse em promoções:", error);
                setNotificacoes(prev => [...prev, `Erro ao cancelar interesse em promoções`]);
            }
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-6xl mx-auto relative">
                <div className="flex flex-col gap-2 absolute -top-6 -right-2 border rounded-lg border-gray-500 text-gray-500 text-sm bg-white max-w-[350px] p-2">
                    {notificacoes.length > 0 ? (notificacoes.map((notificacao, index) => (
                        <div key={index} className="flex flex-row justify-between text-xs border border-gray-500 bg-white text-black px-4 py-2 rounded-lg shadow-md">
                            {notificacao}
                            <button className="px-2 py-1 h-fit hover:bg-red-500/20 hover:cursor-pointer text-center place-self-end border border-gray-500 rounded-lg " onClick={() => {
                                setNotificacoes(notificacoes.filter((_, i) => i !== index))
                            }}>
                                Excluir
                            </button>
                        </div>
                    ))) : "Sem notificações"}
                </div>
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
                        <div className="flex flex-col gap-2">
                            {!isSubscribed ? (
                                <input
                                    type="text"
                                    placeholder="Informe seu nome para receber promoções"
                                    value={clienteId}
                                    className="border rounded-md text-black h-fit p-2"
                                    onChange={(e) => setClienteId(e.target.value)}
                                    disabled={isSubscribed}
                                />
                            ) : (
                                <p className="text-sm text-gray-500">Cliente: {clienteId}</p>
                            )}
                            <div className="flex flex-row gap-2">
                                <button
                                    disabled={!clienteId || isSubscribed}
                                    onClick={handlePromocao}
                                    className="hover:cursor-pointer bg-green-500 text-sm inline-flex items-center px-6 py-3 text-white rounded-md hover:bg-green-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Desejo receber promoções
                                </button>
                                <button
                                    disabled={!isSubscribed}
                                    onClick={handleCancelarPromocao}
                                    className="hover:cursor-pointer text-sm bg-red-500 inline-flex items-center px-6 py-3 text-white rounded-md hover:bg-red-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Desativar notificações de promoção
                                </button>
                            </div>
                        </div>
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
                                className="hover:cursor-pointer w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
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
                                            Cabines Disponíveis:
                                        </span>
                                        <span className="text-sm text-gray-900">
                                            {itinerario.cabines_disponiveis}
                                        </span>
                                    </div>
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
                                            {itinerario.datas_embarque.join(", ")}
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
                                        <button className="hover:cursor-pointer w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors">
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
