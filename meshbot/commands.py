"""Registro de comandos. Handler: (ctx, args) -> texto curto (<= 60 chars).

Para adicionar um comando na próxima etapa: crie cmd_<nome> e registre em COMMANDS.
"""

from dataclasses import dataclass
from typing import Callable

from meshbot.clima import clima_texto
from meshbot.inmet import alerta_texto


@dataclass(frozen=True)
class BotContext:
    """Dados para os handlers. Etapa 1: vazio; /hora trará 'now' etc."""


Handler = Callable[[BotContext, list[str]], str]


def cmd_teste(ctx: BotContext, args: list[str]) -> str:
    return "Teste recebido com sucesso!"


def cmd_alerta(ctx: BotContext, args: list[str]) -> str:
    return alerta_texto()


def cmd_clima(ctx: BotContext, args: list[str]) -> str:
    return clima_texto()


def cmd_help(ctx: BotContext, args: list[str]) -> str:
    linhas = [f"/{n} - {HELP.get(n, '?')}" for n in sorted(COMMANDS) if n != "help"]
    return "\n".join(linhas)


TEL = """190 - Polícia Militar
192 - SAMU
193 - Corpo de Bombeiros
199 - Defesa Civil
180 - Central de Atendimento à Mulher
188 - CVV - Centro de Valorização da Vida"""


def cmd_tel(ctx: BotContext, args: list[str]) -> str:
    return TEL


RPT = """Mirassol - 147.390 | +600 | Sub 123.0
SJRP - 439.125 | -5000 | Sub 71.9
Cedral - 439.725 | -5000 | Sub 100
SJRP 2 - 439.275 | -5000 | Sub 123"""


def cmd_rpt(ctx: BotContext, args: list[str]) -> str:
    return RPT


HELP: dict[str, str] = {
    "alerta": "avisos INMET p/ SJRP",
    "clima": "agora + previsao 2 dias",
    "rpt": "repetidoras radioamador sjrp",
    "tel": "telefones de emergencia",
    "teste": "teste de recebimento",
}


COMMANDS: dict[str, Handler] = {
    "alerta": cmd_alerta,
    "clima": cmd_clima,
    "help": cmd_help,
    "rpt": cmd_rpt,
    "tel": cmd_tel,
    "teste": cmd_teste,
}
