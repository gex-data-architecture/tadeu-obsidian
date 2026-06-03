---
tipo: limpeza
schema: instituto_experience
data: 2026-06-03
status: executado-2026-06-03-28-tabelas-dropadas
tags: [limpeza, manutencao, lint]
gerado_por: skill/limpeza-banco
---
# Limpeza de tabelas vazias — `instituto_experience`

> Análise gerada pela skill `limpeza-banco` em **2026-06-03**. Schema vivo, MySQL/RDS.
> **Nada foi apagado.** Scripts em `[[limpeza-quarentena.sql]]` e `[[limpeza-drop-datado.sql]]`
> — quem executa é o DBA. O MCP é read-only por design.

## Resultado

**28 tabelas** candidatas (recorte aprovado pelo time). Critérios atendidos:

| Critério                                                         | Status                                                                   |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `COUNT(*) = 0` **real** (não estimativa)                         | ✅ confirmado                                                             |
| não é `_stage` / `_old` (swap atômico)                           | ✅ regra travada                                                          |
| sem referência em procedure/function/event/view                  | ✅ confirmado                                                             |
| sem FK externa apontando / sem trigger                           | ✅ (só FK interna `affiliate_products`→`affiliate_details`)               |
| sem **escrita** (`UPDATE_TIME` NULL, janela ~7,7 dias de uptime) | ✅ confirmado                                                             |
| sem **leitura** externa (Looker/n8n/app)                         | ❓ **não confirmável** — `tadeu_lopes` sem acesso ao `performance_schema` |

A leitura externa não pôde ser provada (sem `performance_schema`), mas o time
avaliou este recorte como **conjunto conhecido e de baixo risco** e optou por
**DROP direto** (sem a etapa de quarentena). O caminho está em
`[[limpeza-drop-datado.sql]]` — **backup `mysqldump` é obrigatório no PASSO 0**,
pois o DROP é irreversível. A quarentena por RENAME (`[[limpeza-quarentena.sql]]`)
fica **reservada para o próximo lote** (tabelas mais arriscadas, ver abaixo).

## As 28 por grupo

**Django/auth — app desativado (7)**
`auth_group` · `auth_group_permissions` · `auth_permission` · `auth_user` · `auth_user_groups` · `auth_user_user_permissions` · `django_content_type`

**Temp / scratch / teste (4)**
`tbl_teste` · `temp_event_sucess_commited` · `temp_event_sucess_salesbound` *(17 MB alocados, 0 linhas)* · `temp_leads_slicktext`

**Clickbank affiliate vazias (3)**
`clickbank_affiliate` · `clickbank_affiliate_usd` · `clickbank_nutra_usd`

**Exports de campanhas antigas (3)**
`cmp_c01_nov_2024_leads_oneclick` · `fm5d_c01_out_2024_leads` · `leads_cev_c08_jan_202`

**Features de app não usadas (11)**
`abandoned_carts` · `affiliate_details` · `affiliate_products` · `campaign_click` · `customers` · `historywhatsapp` · `lead_events_target` · `listas_sms_aux` · `sla_alerts_sent` · `telegram_messages` · `whatsapp_reports`

⚠️ Ordem FK: `affiliate_products` antes de `affiliate_details` (FK `affiliate_products_ibfk_1`). Os scripts já tratam com `FOREIGN_KEY_CHECKS=0`.

## Fora do recorte (analisadas, mas mantidas)

- **Alvos de swap `_aws_new` (investigados → NÃO entram nunca):** `clickbank_physical_new_aws_new` (criada hoje), `gold_clickbank_aws_new`, `dashboard_channels_marketing_aws_new`. Estão vazias porque são o **alvo do swap atômico**, irmãs das tabelas vivas `clickbank_physical_new_aws` (330k, escrita hoje), `gold_clickbank_aws` (216k, escrita hoje) e `dashboard_channels_marketing_aws` (47k). Mesma armadilha de `_stage`/`_old`.
- **Tinham 1 linha** (estimador dizia 0): `cbc_c02_mar_2025_leads_oneclick`, `clickbank_fee_rates`, `contatos_captura1x1`, `django_migrations`, `duelab_sessions`, `general_product_costs`, `regime_config`, `setup_carteirinha`, `v2cmp_c01_nov_2024_leads_oneclick`, `web_users`.
- **Todas as `_stage`, `_old` e `_aws_new`** — partes do swap atômico, nunca entram.

## Lote 2 — quarentena (5 tabelas, script `[[limpeza-quarentena.sql]]`)

Órfãs de dashboard/gold, todas conferidas em 2026-06-03: `COUNT(*)=0` real, sem
irmão de swap vivo, sem ref. estática, sem FK, sem trigger, `UPDATE_TIME` NULL.
Única incógnita = **leitura externa** (Looker/n8n) — por isso vão para **quarentena
por RENAME** (`_zzdrop_`), não DROP direto:

`clickbank_physical_v2` · `dashboard_cartpanda_pais_diario` · `dashboard_dim_gestorl` · `dashboard_gerenciador_unificado` · `dashboard_partner_affiliates`

## Como fechar a leitura (opcional, dá um DROP direto)

Peça ao DBA o GRANT abaixo; depois a skill roda a checagem de I/O real e crava quem
lê. Se ninguém lê nenhuma das 27, pula a quarentena.
```sql
GRANT SELECT ON performance_schema.table_io_waits_summary_by_table TO 'tadeu_lopes'@'%';
```

## Próximos passos

**Lote 1 — as 28 (DROP direto, aprovado):**
1. DBA roda o PASSO 0 de `[[limpeza-drop-datado.sql]]` (backup `mysqldump`); confere o `.sql` gerado (> 0 bytes).
2. DBA roda o PASSO 1 (DROP FK-safe) e o PASSO 2 (conferência: 0 linhas).

**Lote 2 — quarentena (próximo, tabelas mais arriscadas):**
3. Investigar quem criou `clickbank_physical_new_aws_new` (CREATE_TIME hoje) **antes** de qualquer ação.
4. Para os `dashboard_*` órfãos, `gold_clickbank_aws_new` e `clickbank_physical_v2`: RENAME → `_zzdrop_`
   (`[[limpeza-quarentena.sql]]` como template), observar 1–2 semanas, depois DROP.
5. (Opcional) Views quebradas: rodar o passo de views da skill à parte.

## Relacionados
[[00-Indice]] · [[migracao-data_team-mapa]] · skill `limpeza-banco`
