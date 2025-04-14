from app.ms_marketing.publisher import publicar_promocao

if __name__ == "__main__":

    promocoes = [
        {
            "mensagem": "Cruzeiro no Caribe com 25% OFF!",
            "destino": "Caribe",
            "valido_ate": "2025-04-20",
        },
        {
            "mensagem": "Cruzeiro na Europa com 15% OFF!",
            "destino": "Europa",
            "valido_ate": "2025-06-30",
        },
        {
            "mensagem": "Cruzeiro no Brasil com 40% OFF!",
            "destino": "Brasil",
            "valido_ate": "2025-05-10",
        },
    ]

    for promocao in promocoes:
        publicar_promocao(promocao)
