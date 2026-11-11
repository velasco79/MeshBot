# 02 — Referência de comandos

## Regras gerais (valem para todos)

- **Gatilho:** mensagem começada com `/` (após `strip()`); nome case-insensitive
  (`/CLIMA` = `/clima`); argumentos separados por espaço (v1 os ignora).
- **Texto sem `/` é ignorado silenciosamente** — o bot nunca interfere em conversa.
- **Rate limit:** 1 resposta por node a cada 10 s (anti-flood; o 2º comando
  consecutivo é ignorado e registrado no log).
- **Anti-loop:** mensagens do próprio node são ignoradas.
- **Onde responde:** chamado por PM → responde por PM; chamado em canal →
  responde no mesmo canal (LongFast = índice 0).
- **Comando desconhecido:** `comando /xyz desconhecido` (sujeito ao rate limit).
- **Teto de tamanho:** mono-linha até 60 caracteres; respostas multi-linha
  até 228 (1 pacote). Acima disso, `bot.py` quebra em blocos de ≤ 228 bytes
  (a lib não fragmenta sozinha — ver docs/04).

## `/teste`

Confirmação de enlace (padrão das comunidades: OKMesh `test`, 868meshbot `#test`).

```
Teste recebido com sucesso!
```

## `/alerta`

Avisos meteorológicos **oficiais do INMET** ativos para São José do Rio Preto
(filtro pelo código IBGE `3549805` no campo `geocodes` do aviso).

| Situação | Resposta |
|---|---|
| Sem aviso ativo | `sem alertas INMET p/ SJRP (emergencia: 199)` |
| Aviso ativo | `INMET <cor>: <fenômeno> ate <dd/mm hh:mm>` |
| API fora do ar | `alertas indisponíveis` |

- `<cor>`: `amarelo` (perigo potencial) · `laranja` (perigo) · `vermelho` (grande perigo)
- Havendo vários avisos, responde o **mais severo** (vermelho > laranja > amarelo).
- Exemplo real (alerta de 15/10/2026): `INMET laranja: Tempestade ate 15/10 23:59`

### Push automático de alerta vermelho

Independente de pedidos, um aviso **VERMELHO** ativo para SJRP é difundido no
canal LongFast **1× por período**: manhã (≥08h), tarde (≥14h), noite (≥20h).
Verificação a cada 30 min (respeita o cache da API). Amarelo/laranja nunca são
difundidos proativamente — decisão de etiqueta alinhada à prática das comunidades
(difusão automática só para grande perigo).

## `/clima`

Três linhas — cidade, condição atual (Open-Meteo) e previsão oficial INMET:

```
Cidade: SJRP
T:27C | U: 39% | V: 11km/h
Hoje: 16-26C | Amanha: 14-27C
```

| Linha | Fonte | Observação |
|---|---|---|
| `Cidade:` | constante `CIDADE` em `clima.py` | cidade fixa do bot (SJRP) |
| `T: / U: / V:` | Open-Meteo (condição atual) | temperatura, umidade relativa e vento (km/h), arredondados |
| `Hoje: / Amanha:` | INMET oficial (`/previsao/3549805`) | mín-máx achatados dos turnos (manhã/tarde/noite) |
| Qualquer fonte falhando | — | `clima indisponível` |

Total ~69 chars em 3 linhas = 1 packet (teto 228). A descrição de condição
(limpo/chuva…) saiu do formato na reformatada de 18/10 — o mapa WMO foi removido junto.

## `/tel`

Telefones de emergência, um por linha (versão compacta de 18/10, 160 bytes =
1 pacote):

```
190 - Polícia Militar
192 - SAMU
193 - Corpo de Bombeiros
199 - Defesa Civil
180 - Central de Atendimento à Mulher
188 - CVV - Centro de Valorização da Vida
```

## `/rpt`

Repetidoras de radioamador da região (dados informados pelo dono do projeto,
18/10 — revisar se alguma mudar):

```
Mirassol - 147.390 | +600 | Sub 123.0
SJRP - 439.125 | -5000 | Sub 71.9
Cedral - 439.725 | -5000 | Sub 100
SJRP 2 - 439.275 | -5000 | Sub 123
```

Formato: `cidade - frequência MHz | deslocamento kHz | tom de sub-banda`.
140 bytes = 1 pacote.

## `/help`

Menu de todos os comandos, um por linha, gerado automaticamente do registro
(`HELP` em `commands.py` — comando novo aparece aqui sem trabalho extra; um
teste quebra se alguém registrar comando sem descrição). Saída de hoje:

```
/alerta - avisos INMET p/ SJRP
/clima - agora + previsao 2 dias
/rpt - repetidoras radioamador sjrp
/tel - telefones de emergencia
/teste - teste de recebimento
```

> Exceção documentada à regra dos 60 chars: menu multi-linha (~140 bytes com
> 5 comandos, ainda 1 packet de 228). O rate limit de 10 s protege contra flood.

Comando desconhecido responde `comando /xyz desconhecido (use /help)`.

## Comandos em backlog (Etapa 2+)

~~`/cmd`~~ (substituído por `/help`, implementado) · `/hora` ·
`/ping` (SNR/hops do próprio pacote) · `/malha` (nº de nodes) · `/umidade`
(níveis de URA da Defesa Civil de Rio Preto) · BBS store-and-forward.
Ver `docs/06` e `docs/07`.
