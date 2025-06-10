import { useState, useEffect } from "react";
import { Link } from "react-router";

// Tipos para o sistema de reservas
interface Reserva {
    reserva_id: string;
    cliente_id: string;
    numero_passageiros: number;
    numero_cabines: number;
    data_embarque: string;
    valor: number;
    status_pagamento: string;
    status_bilhete: string;
    data_criacao: string;
    status?: string;
}

export function meta() {
    return [
        { title: "Status das Reservas - Sistema de Cruzeiros" },
        {
            name: "description",
            content: "Visualize o status de todas as reservas de cruzeiros",
        },
    ];
}

export default function Status() {
    const [reservas, setReservas] = useState<Reserva[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Função para carregar as reservas
    const carregarReservas = async () => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch('http://localhost:5001/api/reservas');
            
            const data = await response.json();
            
            if(data)
                setReservas(data);
            else
                setReservas([])
            
        } catch (err) {
            console.error('Erro ao carregar reservas:', err);
            setError('Erro ao conectar com o servidor');
        } finally {
            setLoading(false);
        }
    };

    // Carregar reservas ao montar o componente
    useEffect(() => {
        carregarReservas();
    }, []);

    // Função para formatar valores monetários
    const formatarValor = (valor: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    };

    // Função para formatar data
    const formatarData = (data: string) => {
        return new Date(data).toLocaleDateString('pt-BR');
    };

    // Função para obter cor do status
    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'pagamento_aprovado':
            case 'aprovado':
                return 'text-green-600 bg-green-100';
            case 'pagamento_pendente':
            case 'pendente':
                return 'text-yellow-600 bg-yellow-100';
            case 'pagamento_recusado':
            case 'recusado':
                return 'text-red-600 bg-red-100';
            case 'bilhete_gerado':
                return 'text-blue-600 bg-blue-100';
            case 'cancelada':
                return 'text-gray-600 bg-gray-100';
            default:
                return 'text-gray-600 bg-gray-100';
        }
    };

    // Função para cancelar reserva
    const cancelarReserva = async (reserva_id: string) => {
        if (!window.confirm('Tem certeza que deseja cancelar esta reserva?')) return;
        try {
            const response = await fetch(`http://localhost:5001/api/reservas/${reserva_id}/cancelar`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                const data = await response.json();
                alert(data.erro || 'Erro ao cancelar reserva');
            } else {
                alert('Reserva cancelada com sucesso!');
                carregarReservas();
            }
        } catch (err) {
            alert('Erro ao conectar com o servidor');
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Carregando reservas...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-red-600 text-xl mb-4">❌ Erro</div>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={carregarReservas}
                        className="hover:cursor-pointer px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200"
                    >
                        Tentar Novamente
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Status das Reservas
                    </h1>
                    <p className="text-xl text-gray-600">
                        Acompanhe todas as reservas do sistema
                    </p>
                </div>

                {/* Navigation */}
                <div className="mb-6">
                    <Link
                        to="/"
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200"
                    >
                        ← Voltar para Home
                    </Link>
                </div>

                {/* Refresh Button */}
                <div className="mb-6 flex justify-end">
                    <button
                        onClick={carregarReservas}
                        className="hover:cursor-pointer inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition duration-200"
                    >
                        🔄 Atualizar
                    </button>
                </div>

                {/* Content */}
                {reservas.length > 0 ? (
                    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Reserva ID
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Cliente
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Passageiros
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Cabines
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Data de Embarque
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Valor
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status Pagamento
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status Bilhete
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Ações
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {reservas.map((reserva) => (
                                        <tr key={reserva.reserva_id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {reserva.reserva_id.substring(0, 8)}...
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {reserva.cliente_id}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {reserva.numero_passageiros}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {reserva.numero_cabines}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {formatarData(reserva.data_embarque)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                                                {formatarValor(reserva.valor)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(reserva.status_pagamento)}`}>
                                                    {reserva.status_pagamento.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(reserva.status_bilhete)}`}>
                                                    {reserva.status_bilhete.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <button
                                                    onClick={() => cancelarReserva(reserva.reserva_id)}
                                                    className="hover:cursor-pointer px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-xs"
                                                >
                                                    Cancelar
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        
                        {/* Footer da tabela */}
                        <div className="bg-gray-50 px-6 py-3">
                            <p className="text-sm text-gray-700">
                                Total de reservas: <span className="font-medium">{reservas.length}</span>
                            </p>
                        </div>
                    </div>
                ) : (
                    /* Estado vazio */
                    <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                        <div className="text-gray-400 text-6xl mb-4">📋</div>
                        <h3 className="text-2xl font-medium text-gray-900 mb-2">
                            Nenhuma reserva encontrada
                        </h3>
                        <p className="text-gray-600 mb-6">
                            Não há reservas cadastradas no sistema ainda.
                        </p>
                        <Link
                            to="/"
                            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200"
                        >
                            Fazer uma Reserva
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
}
