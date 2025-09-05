import requests
import json
import time
from lista_stickers import STICKERS


# Arquivo JSON de saída
JSON_SAIDA = "stickers_data.json"


# Função para pegar preço atual
def obter_preco(nome_item):
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "country": "BR",
        "currency": 7,
        "appid": 730,
        "market_hash_name": nome_item
    }

    while True:
        try:
            r = requests.get(url, params=params)
            if r.status_code == 429:
                print("Muitas requisições. Aguardando 30 segundos para tentar novamente...")
                time.sleep(30)
                continue
            elif r.status_code != 200:
                return None

            data = r.json()
            preco_str = data.get("lowest_price")
            if not preco_str:
                return None

            # Remove símbolos e formata para float
            preco = float(preco_str.replace("R$ ", "").replace(".", "").replace(",", "."))
            return preco
        except Exception as e:
            print(f"Erro ao obter preço para {nome_item}: {e}")
            return None


# Carrega dados iniciais (preço inicial e quantidade)
def carregar_dados_iniciais():
    dados_iniciais = {}
    try:
        with open("dados_iniciais.json", "r", encoding="utf-8") as f:
            dados_iniciais = json.load(f)
    except FileNotFoundError:
        # Se o arquivo não existe, criamos com valores padrão
        for sticker in STICKERS:
            dados_iniciais[sticker] = {
                "preco_inicial": 0,
                "quantidade": 1
            }
        salvar_dados_iniciais(dados_iniciais)

    return dados_iniciais


# Salva dados iniciais
def salvar_dados_iniciais(dados):
    with open("dados_iniciais.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# Gera o JSON no formato esperado pelo Flutter
def gerar_json(dados_iniciais, precos_atuais):
    resultado = {}

    for sticker in STICKERS:
        preco_atual = precos_atuais.get(sticker)
        if preco_atual is None:
            continue

        dados = dados_iniciais.get(sticker, {"preco_inicial": 0, "quantidade": 1})
        preco_inicial = dados["preco_inicial"]
        quantidade = dados["quantidade"]

        # Calcula a porcentagem de valorização
        if preco_inicial > 0:
            porcentagem = ((preco_atual - preco_inicial) / preco_inicial) * 100
        else:
            porcentagem = 0

        resultado[sticker] = [{
            "preço_inicial": preco_inicial,
            "preco": preco_atual,
            "porcentagem": round(porcentagem, 2),
            "quantidade": quantidade
        }]

    return resultado


def main():
    print("Iniciando coleta de preços...")

    # Carrega dados iniciais
    dados_iniciais = carregar_dados_iniciais()
    precos_atuais = {}

    # Obtém preços atuais
    for i, sticker in enumerate(STICKERS):
        print(f"{i + 1}/{len(STICKERS)} - Obtendo preço para: {sticker}")
        preco = obter_preco(sticker)

        if preco is not None:
            precos_atuais[sticker] = preco
        else:
            print(f"  Erro ao obter preço para {sticker}")

        # Espera para não sobrecarregar a API
        time.sleep(1.5)

    # Gera o JSON final
    json_final = gerar_json(dados_iniciais, precos_atuais)

    # Salva o JSON
    with open(JSON_SAIDA, "w", encoding="utf-8") as f:
        json.dump(json_final, f, ensure_ascii=False, indent=2)

    print(f"JSON gerado: {JSON_SAIDA}")
    print("Processo concluído!")


if __name__ == "__main__":
    main()