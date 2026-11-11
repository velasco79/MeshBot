# 05 — Desenvolvimento

## Ambiente

```bash
cd ~/meshbot
~/.venvs/meshbot/bin/python -m pytest -q      # suíte (42 testes)
~/.venvs/meshbot/bin/python -m pytest tests/test_clima.py -q   # um arquivo
```

Identidade git é **local ao repositório** (`git config user.name/email`, sem
`--global`). Commits pequenos e frequentes, um por tarefa.

## Ciclo TDD (obrigatório para lógica)

1. Escrever o teste que falha → rodar e **confirmar a falha**.
2. Implementar o mínimo → rodar e confirmar `passed`.
3. Suíte completa verde → commit.

Exceção: `bot.py`/`__main__.py` (cola fina) são validados contra o rádio real.

## Como adicionar um comando

Três passos. Exemplo de um `/algo` hipotético:

**1.** Lógica pura com dependência injetável (novo módulo ou reaproveitado):

```python
# meshbot/algo.py
def algo_texto(fetch=fetch_json) -> str:
    try:
        ...
        return "resposta <= 60 chars"
    except Exception:
        return "algo indisponível"
```

**2.** Handler + registro em `meshbot/commands.py`:

```python
def cmd_algo(ctx: BotContext, args: list[str]) -> str:
    return algo_texto()

COMMANDS: dict[str, Handler] = {
    ...
    "algo": cmd_algo,
}
```

**3.** Testes em `tests/test_algo.py` com fetch fake (caso feliz, erro de rede,
limite de 60 chars). Dados de API **nunca** são chamados nos testes.

Regras que todo comando deve respeitar: resposta ≤ 60 chars · falha de fonte →
mensagem curta (nunca exceção) · dados locais primeiro (o que vale para
Oklahoma pode não valer para SJRP — ver `docs/07`).

## Injetando dados do pacote/rádio no handler

`BotContext` (em `commands.py`) é o ponto único: adicionar campo com default →
preencher em `MeshBot._context(packet)` → usar no handler. Defaults preservam
compatibilidade com testes existentes.

## Convenções

- Código e comentários em português; mensagens de resposta sem acentos quando
  economizam bytes sem perder clareza (`emergencia`, `amanha`).
- Constantes de SJRP/INMET em `meshbot/inmet.py` e `meshbot/clima.py`
  (IBGE, lat/lon, cores, URLs) — não duplicar.
- `bot.log`, `__pycache__/` e `*.pyc` fora do git (`.gitignore`).
- Toda API nova: timeout de 5 s e User-Agent identificando o bot.
