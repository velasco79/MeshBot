"""Comando /clima — condição atual (Open-Meteo) + previsão INMET, 3 linhas.

Ex.:
    Cidade: SJRP
    T:27C | U: 39% | V: 11km/h
    Hoje: 16-26C | Amanha: 14-27C
Qualquer fonte falhando -> resposta curta única (consistente com /alerta).
"""

from .inmet import fetch_json

LAT, LON = -20.8113, -49.3758  # São José do Rio Preto/SP
URL_AGORA = (
    f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    "&timezone=America/Sao_Paulo"
)
URL_PREVISAO = "https://apiprevmet3.inmet.gov.br/previsao/3549805"
CIDADE = "SJRP"  # São José do Rio Preto/SP — cidade fixa do bot
INDISPONIVEL = "clima indisponível"


def _minmax_diario(dia: dict) -> tuple[int, int]:
    """Achata os dois formatos do INMET: por turno (manha/tarde/noite) ou diário."""
    if "temp_min" in dia:
        return int(dia["temp_min"]), int(dia["temp_max"])
    turnos = [t for t in ("manha", "tarde", "noite") if t in dia]
    return (min(int(dia[t]["temp_min"]) for t in turnos),
            max(int(dia[t]["temp_max"]) for t in turnos))


def clima_texto(fetch_agora=fetch_json, fetch_inmet=fetch_json) -> str:
    try:
        cur = fetch_agora(URL_AGORA)["current"]
        previsao = fetch_inmet(URL_PREVISAO)["3549805"]
        dias = list(previsao.values())
        hoje_min, hoje_max = _minmax_diario(dias[0])
        am_min, am_max = _minmax_diario(dias[1])
        texto = (
            f"Cidade: {CIDADE}\n"
            f"T:{round(cur['temperature_2m'])}C "
            f"| U: {round(cur['relative_humidity_2m'])}% "
            f"| V: {round(cur['wind_speed_10m'])}km/h\n"
            f"Hoje: {hoje_min}-{hoje_max}C | Amanha: {am_min}-{am_max}C"
        )
        return texto[:228]
    except Exception:
        return INDISPONIVEL
