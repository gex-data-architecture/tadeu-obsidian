---
name: organizar-eventos
description: Separa as notas de eventos do MySQL no vault em duas subpastas — `Eventos/ENABLE` (só os eventos ATIVOS) e `Eventos/DISABLE` (inativos) — lendo o STATUS real do banco (`information_schema.EVENTS`). Use SEMPRE que o usuário falar em "separar eventos", "organizar eventos", "eventos ativos/inativos", "eventos habilitados/desabilitados", "ENABLE/DISABLE", "quais events estão rodando", "deixar só os eventos ativos numa pasta", ou logo após alguém ligar/desligar um event no banco (para o vault refletir) — mesmo sem dizer a palavra "skill". É SOMENTE LEITURA no MySQL (via creds do MCP `mysql`); só move arquivos markdown, nunca altera o banco. Schema padrão: `instituto_experience` (parametrizável).
---

# organizar-eventos

Mantém as notas de eventos do vault espelhando o **status real do MySQL**: os
eventos **ATIVOS** ficam em `Eventos/ENABLE/` e os **inativos** em `Eventos/DISABLE/`.
Assim dá pra olhar a pasta `ENABLE` e saber, de relance, **o que está rodando de fato**.

## Quando usar
- Pedido direto: "separa os eventos em ativos e inativos", "deixa só os ativos no ENABLE".
- Depois de **ligar/desligar** um event no banco (`ALTER EVENT ... ENABLE/DISABLE`) — rodar de
  novo re-sincroniza (um event que virou DISABLED migra de `ENABLE` → `DISABLE` sozinho).
- Depois de regenerar o vault com o `3_gerar_vault.py` (ele já escreve direto nas subpastas,
  mas rodar isto garante a consistência se algo ficou no formato plano).

## Como funciona (fonte da verdade = o banco)
1. Consulta `information_schema.EVENTS` (READ-ONLY) para o schema alvo → `EVENT_NAME` + `STATUS`.
2. Para cada evento, acha a nota `<EVENT_NAME>.md` (esteja ela plana em `Eventos/` ou já numa subpasta)
   e a move para o balde certo: **`ENABLED` → `ENABLE/`**, qualquer outro status (`DISABLED`,
   `SLAVESIDE_DISABLED`) **→ `DISABLE/`**.
3. Remove cópias duplicadas e **avisa** sobre: eventos do banco sem nota no vault (rode o gerador)
   e notas `.md` sem evento correspondente no banco (event dropado).

Não toca no conteúdo das notas nem no banco — só **realoca arquivos**. Os `[[wikilinks]]` do
Obsidian são por nome de arquivo, então mover de pasta **não quebra link nenhum**; o Dataview que
lê `FROM ".../Eventos"` continua pegando tudo (varre subpastas).

## Como rodar
```powershell
python "C:\Users\tadeu\DataTeamDocs\.claude\skills\organizar-eventos\scripts\organizar_eventos.py"
# outro schema:
python "...\organizar_eventos.py" data_team
```
Requer `pymysql` e as credenciais do MySQL no `.claude.json` (servidor MCP `mysql`).

## Estrutura resultante
```
Banco de Dados/MySQL/<schema>/Eventos/
├── ENABLE/    (somente eventos com STATUS = ENABLED)
└── DISABLE/   (DISABLED / SLAVESIDE_DISABLED)
```

## Após rodar
- Acrescente uma linha no `log.md` (append-only) com a contagem ENABLE/DISABLE.
- O gerador `3_gerar_vault.py` já cria as notas direto em `ENABLE`/`DISABLE` (mesma regra),
  então o split se mantém nas regerações.
