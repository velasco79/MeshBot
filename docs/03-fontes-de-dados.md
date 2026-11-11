# 03 — Fontes de dados

Tudo verificado ao vivo em 2026-10-18 (requisições reais registradas nesta data).

## Em uso

### INMET — `apiprevmet3.inmet.gov.br` (fonte oficial, sem chave)

| Endpoint | Retorna | Usado por |
|---|---|---|
| `GET /avisos/ativos` | Avisos em vigor: `{hoje:[], futuro:[]}`; por aviso: `aviso_cor`, `descricao`, `data_fim`, `hora_fim`, `geocodes` (lista de códigos IBGE afetados) | `/alerta`, push vermelho |
| `GET /previsao/3549805` | Previsão oficial de 5 dias para SJRP | `/clima` |

**Armadilhas confirmadas:**
- ⚠️ **Exige header `User-Agent`** — sem ele a API responde vazio (sem erro!).
- ⚠️ O parâmetro `?uf=SP` em `/avisos/ativos` **não filtra** — vem o Brasil todo;
  o filtro correto é `IBGE_SJRP in geocodes`.
- ⚠️ `/previsao/{ibge}` tem **formato misto**: hoje/amanhã vêm aninhados por
  turno (`manha`/`tarde`/`noite`); dias 3–5 são diários com campos extras
  (`umidade_min/max`, `nascer`, `ocaso`). Parser precisa tratar as duas formas
  (ver `clima._minmax_diario`).
- Cores oficiais: `#FFFE00` amarelo · `#FF7405` laranja · `#DD000B` vermelho.
- Rotas quebradas/inexistentes: `/docs`, `/avisos?codigoUF=`, `/estacoes/SP`,
  `/clima/{ibge}`, `/previsao/ativos` (erro SQL).

### Open-Meteo — `api.open-meteo.com` (sem chave)

`GET /v1/forecast?latitude=-20.8113&longitude=-49.3758&current=temperature_2m,
relative_humidity_2m,weather_code,wind_speed_10m&timezone=America/Sao_Paulo`

Usado pelo `/clima` para a **condição atual** (o INMET não fornece "agora").
Códigos de condição = WMO (mapa em `clima.WMO`).

## Consideradas e descartadas (com o motivo)

| Fonte | Situação (verificada 2026-10-18) |
|---|---|
| **RadarMeteorológico** `radarmeteorologico.com.br/api/v1` | Espelho público do INMET sem chave (`/alertas`, `/temperaturas`, `/cidades`). Funciona, mas o INMET oficial foi escolhido como fonte primária; mantém-se como **fallback candidato**. |
| **Cemaden** (alertas de inundação/deslizamento) | Painel público (`painelalertas.cemaden.gov.br`), **sem API** — `api.cemaden.gov.br` nem resolve DNS. |
| **Defesa Civil Estadual SP** | Sem API; serviço público é SMS: enviar CEP para **40199**. |
| **Defesa Civil Municipal SJRP** | Sem API/feed; boletins viram notícia no site da prefeitura. Contatos: **199** (24h via GCM), (17) 3211-1730, defesacivil@riopreto.sp.gov.br. Níveis de URA próprios: Atenção 30–20%, Alerta 20–12%, Emergência <12% (base do futuro `/umidade`). |
| **S2ID / Atlas Digital de Desastres** | Dados abertos CSV (histórico 1991–2025) — contexto, não tempo real. |

## Constantes de SJRP

```
IBGE     3549805
latitude -20.8113
longitude -49.3758
fuso     America/Sao_Paulo (-03)
```

## Política de uso

- Respeitar caches das APIs (INMET ~10 min → tick do push de 30 min).
- Timeout de 5 s em toda requisição; falha vira resposta curta, nunca exceção no ar.
- Em emergência real, a autoridade é INMET/Defesa Civil (**199**) — o bot orienta, não substitui.
