"""Avisos meteorológicos oficiais do INMET para São José do Rio Preto.

Fonte primária: apiprevmet3.inmet.gov.br (oficial, sem chave; exige User-Agent).
Em emergência, a fonte oficial é o INMET / Defesa Civil (199).
"""

import json
import urllib.request

IBGE_SJRP = "3549805"
URL = "https://apiprevmet3.inmet.gov.br/avisos/ativos"
SEM_ALERTA = "sem alertas INMET p/ SJRP (emergencia: 199)"
INDISPONIVEL = "alertas indisponíveis"

CORES = {"#FFFE00": "amarelo", "#FF7405": "laranja", "#DD000B": "vermelho"}
RANK = {"vermelho": 3, "laranja": 2, "amarelo": 1}


def fetch_json(url: str = URL, timeout: float = 5.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MeshBot/1.0 (Meshtastic)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _avisos_sjrp(dados: dict) -> list[dict]:
    meus = []
    for periodo in ("hoje", "futuro"):
        for aviso in dados.get(periodo, []):
            geocodes = [g.strip() for g in str(aviso.get("geocodes", "")).split(",")]
            if IBGE_SJRP in geocodes:
                meus.append(aviso)
    return meus


def _cor(aviso: dict) -> str:
    return CORES.get(str(aviso.get("aviso_cor", "")).upper(), "?")


def _texto(aviso: dict) -> str:
    fim = str(aviso.get("data_fim", ""))          # 2026-10-20T00:00:00.000Z
    hora = str(aviso.get("hora_fim", ""))[:5]     # 23:59[:00]
    ate = f"{fim[8:10]}/{fim[5:7]}" if len(fim) >= 10 else "?"
    if hora:
        ate += f" {hora}"
    return f"INMET {_cor(aviso)}: {aviso.get('descricao', '?')} ate {ate}"[:60]


def _mais_severo(avisos: list[dict]) -> dict:
    return max(avisos, key=lambda a: RANK.get(_cor(a), 0))


def alerta_texto(fetch=fetch_json) -> str:
    """Resposta do comando /alerta (<= 60 chars)."""
    try:
        avisos = _avisos_sjrp(fetch())
    except Exception:
        return INDISPONIVEL
    if not avisos:
        return SEM_ALERTA
    return _texto(_mais_severo(avisos))


def vermelho_ativo(fetch=fetch_json) -> str | None:
    """Texto do aviso VERMELHO (grande perigo) ativo para SJRP, ou None."""
    try:
        avisos = [a for a in _avisos_sjrp(fetch()) if _cor(a) == "vermelho"]
    except Exception:
        return None
    return _texto(_mais_severo(avisos)) if avisos else None
