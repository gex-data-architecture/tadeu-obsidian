---
tipo: moc
tags: [moc, conhecimento]
---
# Conhecimento (páginas curadas)

> Esta pasta guarda o conhecimento **durável** — narrativas, dossiês de negócio, decisões,
> relatórios de lint e MOCs. Diferente de `Tabelas/`, `Views/`, `Rotinas/` e `Eventos/`,
> **nada aqui é sobrescrito** pelos scripts de geração. É aqui que a wiki "compõe" com o tempo.

## O que colocar aqui
- **Dossiês**: explicações de negócio de uma tabela/pipeline (ex.: `Dossie-cartpanda.md`), linkando os objetos com `[[...]]`.
- **MOCs** (Maps of Content): índices temáticos, ex.: `MOC-Staging.md`, `MOC-Dashboards.md`.
- **Decisões**: ex.: `Decisao-arquivar-unified_lead_events_new_backup_1.md`.
- **Lint**: relatórios `Lint-YYYY-MM-DD.md`.

## Convenção
Sempre linke das páginas curadas para as notas geradas (`[[cartpanda_physical]]`), assim o
Graph View conecta o conhecimento de negócio à estrutura técnica.

## Subpastas (saber sobre os dados)
| Pasta | Conteúdo | Template |
|---|---|---|
| [[Conhecimento/Dossies/_sobre\|Dossies]] | dossiês de tabela/pipeline | `dossie-tabela` |
| [[Conhecimento/Calls/_sobre\|Calls]] | atas de reunião | `call` |
| [[Conhecimento/Decisoes/_sobre\|Decisoes]] | ADRs | `decisao` |

## Pastas curadas no ROOT (artefatos de trabalho/operação)
Ficam **fora** de `Conhecimento/` por destaque: [[Fluxos-N8N/_sobre\|Fluxos-N8N]],
[[Epicos/_sobre\|Epicos]], [[Incidentes/_sobre\|Incidentes]], [[Pipelines/_sobre\|Pipelines]],
[[API/_sobre\|API]], [[Planilhas Manuais/_sobre\|Planilhas Manuais]].
São igualmente **curadas** (nunca sobrescritas pelos scripts).

## Páginas avulsas
*(MOCs e dossiês que não caem numa subpasta — ex.: [[MOC-Staging]])*
