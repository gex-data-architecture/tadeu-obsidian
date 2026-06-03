---
tipo: indice
tags: [moc, banco]
banco: data_team
status: vazio
criado_em: 2026-06-02
---
# 🧱 Banco `data_team` — marts e tabelas próprias do time

> Banco MySQL/RDS **criado em 2026-06-02** para as tabelas e *marts* construídos pelo
> próprio time de dados (diferente do `instituto_experience`, que é a fonte operacional).

## Estado atual
- **0 tabelas · 0 views · 0 procedures · 0 eventos** (banco recém-criado, ainda vazio).
- Quando os primeiros objetos forem criados, este banco ganha as pastas geradas
  `DB_data_team/Tabelas|Views|Rotinas|Eventos/` — no mesmo padrão do `DB_instituto_experience`.

## Como popular a documentação (quando houver objetos)
1. Criar as tabelas/marts no banco `data_team` (fora daqui — o MCP é **read-only**).
2. Rodar o extrator apontando para o schema `data_team` (precisa parametrizar os scripts — ver abaixo).
3. Rodar a geração do vault: as notas saem em `data_team/...`.
4. Registrar no [[log]].

> ⚠️ Os scripts em `Inventario MSQL/` hoje estão fixos no schema `instituto_experience`.
> Para incluir o `data_team` na regeração, eles precisam virar **multi-schema**
> (parâmetro de banco). Peça ao Claude quando o primeiro mart existir.

## Propósito (lembrete)
- Camada de **trabalho do time**: marts, agregações, tabelas de apoio.
- **Não** misturar com `instituto_experience` (fonte) — daí a separação por pasta-banco.

## Referências
- Schema do vault: [[CLAUDE]]
- Diário de mudanças: [[log]]
- Banco fonte: [[DB_instituto_experience/00-Indice|instituto_experience]]
