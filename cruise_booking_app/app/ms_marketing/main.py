from app.ms_marketing.publisher import publicar_promocao

if __name__ == "__main__":
    promocao = {
        "mensagem": "Cruzeiro no Caribe com 25% OFF!",
        "destino": "Caribe",
        "valido_ate": "2025-04-20",
    }

    publicar_promocao(promocao)
