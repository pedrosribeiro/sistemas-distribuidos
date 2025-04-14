from app.ms_reserva.publisher import publicar_reserva
from app.ms_reserva.service import consultar_itinerarios, criar_reserva

# TODO: Implementar interface Web
if __name__ == "__main__":
    print("=== MS RESERVA ===")

    # destino = input("Destino desejado: ")
    destino = "Caribe"
    # data_embarque = input("Data de embarque (YYYY-MM-DD): ")
    data_embarque = "2025-07-10"
    # porto_embarque = input("Porto de embarque: ")
    porto_embarque = "Santos"

    print("\nBuscando itinerários...")
    itinerarios = consultar_itinerarios(destino, data_embarque, porto_embarque)

    if not itinerarios:
        print("Nenhum itinerário encontrado.")
    else:
        print(f"\nItinerários disponíveis para {destino}:")
        for i, itin in enumerate(itinerarios):
            print(
                f"{i + 1} - {itin['navio']} ({itin['numero_noites']} noites) - R$ {itin['valor_por_pessoa']:.2f}"
            )

        # escolha = int(input("Escolha um itinerário (número): ")) - 1
        escolha = 1
        itin = itinerarios[escolha]

        cliente = input("Nome do cliente: ")
        num_passageiros = int(input("Número de passageiros: "))
        num_cabines = int(input("Número de cabines: "))

        valor_total = itin["valor_por_pessoa"] * num_passageiros

        reserva = criar_reserva(
            itinerario_id=itin["id"],
            data_embarque=data_embarque,
            cliente=cliente,
            num_passageiros=num_passageiros,
            num_cabines=num_cabines,
            valor=valor_total,
        )

        publicar_reserva(reserva)
