---
tipo: pipeline
status: rascunho
origem: instituto_experience
destino: data_team
criado_em: 2026-06-02
tags: [pipeline, migracao, data_team]
---
# 🚚 Mapa de migração — tabelas finais → `data_team`

> **Escopo = banco inteiro.** Migramos **tudo** para o `data_team`: as **finais** geradas pelas
> procedures dos 7 eventos ativos **e** as **24 tabelas fonte** (só lidas) que as alimentam.
> Excluídas apenas as `_stage` (scratch do swap atômico) e as `_old` (lixo do swap).
> ~~_Premissa antiga: fontes ficavam no `instituto_experience`. Revertida em 2026-06-03 a pedido
> ("as só lidas também precisam ser migradas") — agora o `data_team` é auto-suficiente._~~
>
> **Como funciona o swap atômico:** a procedure popula `X_stage`, depois
> `RENAME TABLE X TO X_old, X_stage TO X` → publica `X` instantaneamente. A **final** é o `X`.
>
> 👉 Coluna `novo_nome` **preenchida com sugestão** (nome no `data_team`). Quando aprovar, eu gero o
> script `CREATE TABLE data_team.<novo> LIKE …` + `INSERT … SELECT` (preserva PK/índices/tipos).
> **Total ≈ 44 GB** — sendo ~7 GB de finais + **~36.7 GB de fontes**. ⚠️ Três fontes dominam:
> `unified_lead_events_new` = **26.9 GB**, `meta_ad_id` = **5.6 GB**, `cw_messages_mat` = **3.8 GB**
> (juntas = 36.3 GB, ou seja **99%** do peso das fontes). Vale decidir se migram inteiras ou com recorte.

## 🏷️ Padrão de nomenclatura (proposto)

**Forma:** `tb_<camada>_<dominio>[_<assunto>][_<grão>]` — tudo `snake_case`, minúsculo, domínio em **inglês**, sem sufixo `_v2`.

> **Por que sem `gex_`?** O **schema já é o namespace**: dentro de `data_team` só existe GEX, então `data_team.tb_gex_…`
> diria "time GEX" duas vezes. No data lake o `gex_` se justifica porque o Glue Catalog/conta AWS são **compartilhados**;
> num schema MySQL dedicado, é peso morto. (Se um dia houver um schema multi-produto, aí o prefixo volta a valer.)

| Token | Regra | Porquê |
|---|---|---|
| `tb_` | prefixo fixo de tabela (views seriam `vw_`) | separa objeto de view/MV; ordena junto |
| `<camada>` | `bronze` · `silver` · `gold` · `mart` · `dim` | **definida pela linhagem real** (ver abaixo) |
| `<dominio>` | área de negócio em inglês: `buygoods`, `clickbank`, `support`, `refund`, `leads`, `marketing`, `meta_ads`, `internal`, `costs` | agrupa tabelas irmãs (todas `..._support_*` ficam juntas) |
| `<grão>` | sufixo de granularidade quando aplicável: `_daily` | deixa o grão explícito |

**As 5 camadas (atribuídas pela dependência entre procedures, não pelo nome antigo):**
- **`bronze`** — feeds **crus** ingeridos por pipelines externos (Glue `*-to-mysql`, lambdas, n8n). Só lidos pelas procedures, nunca derivam de outra tabela do banco. Ex.: `cartpanda_physical`, `clickbank_physical`, `lead_events`, `chatwoot_*`, `costs_*`, `meta_ad_id`. ⚠️ **Quem escreve neles é externo** — migrar exige repontar esses pipelines para o `data_team` (ver Decisões).
- **`silver`** — entidades conformadas/limpas que **alimentam** o gold, mas não são dashboard. Lidas de fontes ou do data lake. Ex.: `buygoods_unified`, `clickbank_physical`.
- **`gold`** — fatos de negócio conformados, grão transação/dia, **reutilizáveis** (não derivam de outra tabela final). Ex.: `gold_buygoods`, `gold_clickbank`, `support`, `refund`, `costs_*_daily`.
- **`mart`** — tabelas de **apresentação/derivadas**, construídas **em cima do gold** para um consumo específico. Ex.: `marketing_channels` (deriva de `gold_clickbank_buygoods`), `internal_*`, `affiliate_nutra`, `meta_ads_consolidated`.
- **`dim`** — dimensões/lookups. Ex.: `dim_product`, `dim_funnel`, `dim_clickbank_product`.

> **Por que não chamar tudo de `gold`?** A linhagem mostra hierarquia real:
> ```mermaid
> flowchart LR
>   subgraph silver
>     u[buygoods_unified]; cp[clickbank_physical]; ct[clickbank_tickets]; ma[meta_ads]
>   end
>   subgraph gold
>     gb[gold_buygoods]; gc[gold_clickbank]; gcb[gold_clickbank_buygoods]; sup[support]; ref[refund]; cost[costs_*_daily]
>   end
>   subgraph mart
>     ch[marketing_channels]; ins[internal_sales]; af[affiliate_nutra]; mc[meta_ads_consolidated]
>   end
>   u-->gb; cp-->gc; ct-->ref; gb-->gcb; gc-->gcb
>   gcb-->ch; gcb-->ins; gcb-->af; cost-->ins; ma-->mc
> ```
> `gold_clickbank_buygoods` é **gold** (fato conformado central); o que lê dele (`channels_marketing`, `internal_*`, `affiliate_*`) é **mart**. `data_team` é justamente a camada de entrega/BI (*serving*), então `silver→gold→mart→dim` cai como uma luva.

> ⚠️ = decisão de camada/nome que vale você confirmar (anotei abaixo).

## A) Gold / consolidadas (dashboards principais)
| origem (instituto_experience)       |    MB | gerada via   | camada | **novo_nome (data_team)**       | deriva de                      |
| ----------------------------------- | ----: | ------------ | ------ | ------------------------------- | ------------------------------ |
| `dashboard_gold_clickbank_buygoods` | 425.0 | swap         | gold   | `tb_gold_clickbank_buygoods`    | gold_buygoods + gold_clickbank |
| `dashboard_gold_buygoods`           | 262.9 | swap         | gold   | `tb_gold_buygoods`              | silver buygoods_unified        |
| `dashboard_gold_clickbank`          | 202.8 | swap         | gold   | `tb_gold_clickbank`             | fontes clickbank               |
| `dashboard_affiliate_nutra`         |  56.2 | swap         | mart   | `tb_mart_affiliate_nutra`       | gold_clickbank_buygoods        |
| `dashboard_affiliate_nutra_usd`     |  59.2 | swap         | mart   | `tb_mart_affiliate_nutra_usd`   | gold_clickbank_buygoods        |
| `dashboard_low_end`                 |   3.0 | write direto | mart   | `tb_mart_low_end`               | gold_buygoods + gold_clickbank |
| `tb_gex_buygoods_unified`           | 288.0 | write direto | silver | `tb_silver_buygoods_unified` ⚠️ | data lake (job unified)        |

## B) Atendimento / leads / reembolso
| origem                           |            MB | gerada via   | camada | **novo_nome**                       | deriva de |
| -------------------------------- | ------------: | ------------ | ------ | ----------------------------------- | --------- |
| `dashboard_auditoria_leads`      |         706.0 | swap         | mart   | `tb_mart_leads_audit`           | mart marketing_channels |
| `dashboard_atendimento`          |         180.8 | swap         | gold   | `tb_gold_support`               | fontes chatwoot (`cw_*`) |
| `dashboard_reembolso`            |         136.7 | swap         | gold   | `tb_gold_refund`                | silver clickbank_tickets |
| `dashboard_anomalia_diaria`      |         123.7 | swap         | mart   | `tb_mart_anomaly_daily`         | gold_clickbank_buygoods |
| `dashboard_sla_times`            |         104.7 | swap         | gold   | `tb_gold_support_sla`           | fontes chatwoot |
| `dashboard_leads_alerts`         |          39.6 | swap         | gold   | `tb_gold_leads_alerts`          | fontes leads |
| `dashboard_ranking_agentes`      |           2.5 | swap         | mart   | `tb_mart_support_agent_ranking` | gold support + refund + support_sla |
| `dashboard_lead_events`          |           2.5 | swap         | gold   | `tb_gold_leads_events`          | fontes leads |
| `dashboard_atendimento_backlog`  |           1.5 | swap         | mart   | `tb_mart_support_backlog`       | gold support |
| `dashboard_atendimento_retornos` |           0.1 | swap         | gold   | `tb_gold_support_returns`       | fontes chatwoot |
| `dashboard_reembolso_coortes`    |           0.1 | swap         | gold   | `tb_gold_refund_cohorts`        | fontes refund |
| `dashboard_leads_por_dia`        | 0.0 (153 lin) | write direto | gold   | `tb_gold_leads_daily`           | fontes leads |

## C) Canais / marketing / Meta Ads
| origem | MB | gerada via | camada | **novo_nome** | deriva de |
|---|---:|---|---|---|---|
| `gerenciador_meta_ads_v2` | 2267.0 | swap | silver | `tb_silver_meta_ads` ⚠️ | fontes Meta (granular) |
| `gerenciador_meta_consolidado_v2` | 739.6 | swap | mart | `tb_mart_meta_ads_consolidated` | silver meta_ads + mart meta_ads_sales |
| `gerenciador_meta_vendas_v2` | 10.5 | swap | mart | `tb_mart_meta_ads_sales` | gold_clickbank_buygoods + costs_*_daily |
| `dashboard_channels_marketing` | 76.6 | swap | mart | `tb_mart_marketing_channels` | gold_clickbank_buygoods |
| `dashboard_channels_country_daily` | 2.5 | swap | mart | `tb_mart_marketing_channels_country_daily` | gold_clickbank_buygoods |

## D) Internal sales / funil
| origem | MB | gerada via | camada | **novo_nome** | deriva de |
|---|---:|---|---|---|---|
| `internal_product_v2` | 7.5 | swap | mart | `tb_mart_internal_product` | gold_clickbank_buygoods |
| `internal_funnel_v2` | 5.5 | swap | mart | `tb_mart_internal_funnel` | gold_clickbank_buygoods |
| `dashboard_internal_sales_v2` | 2.5 | swap | mart | `tb_mart_internal_sales` | gold_clickbank_buygoods + costs_*_daily |

## E) Custos diários
| origem | MB | gerada via | camada | **novo_nome** | deriva de |
|---|---:|---|---|---|---|
| `custos_trafego_gestores_diaria` | 0.1 | swap | gold | `tb_gold_costs_traffic_managers_daily` | fontes de custo |
| `custos_conta_agencia_diaria` | 0.1 | swap | gold | `tb_gold_costs_agency_account_daily` | fontes de custo |
| `custos_gerais_diaria` | 0.0 (150 lin) | swap | gold | `tb_gold_costs_general_daily` | fontes de custo |

## F) Dimensões
| origem | linhas | gerada via | camada | **novo_nome** |
|---|---:|---|---|---|
| `dashboard_dim_product` | 120 | write direto | dim | `tb_dim_product` |
| `dashboard_dim_funil` | 40 | write direto | dim | `tb_dim_funnel` |
| `dashboard_dim_gestor` | 11 | write direto | dim | `tb_dim_manager` |
| `dashboard_dim_source` | 9 | write direto | dim | `tb_dim_source` |

## G) Apoio (clickbank / tickets)
| origem                   |    MB | gerada via                        | camada | **novo_nome**                        | obs                                                                    |
| ------------------------ | ----: | --------------------------------- | ------ | ------------------------------------ | ---------------------------------------------------------------------- |
| `clickbank_physical_new` | 304.7 | write direto (UPDATE offer names) | silver | `tb_silver_clickbank_physical`   | dropei o `_new` (entidade vigente)                                     |
| `cb_tickets`             | 134.1 | write direto                      | silver | `tb_silver_clickbank_tickets` ⚠️ | `cb`→`clickbank`; confirmar se é ticket de clickbank ou de atendimento |
| `clickbank_products`     |   3.1 | write direto                      | dim    | `tb_dim_clickbank_product`       | é referência/lookup de produto                                         |

## H) Fontes cruas — bronze (feeds ingeridos por pipelines externos)
> ⚠️ Estas tabelas **não são geradas pelas procedures** — são alimentadas por jobs Glue `*-to-mysql`,
> lambdas e n8n. Migrar = **repontar esses produtores** para escreverem no `data_team` (ver Decisões §6).

| origem (instituto_experience) |        MB |   linhas | domínio | **novo_nome (data_team)**            | quem escreve / obs |
| ----------------------------- | --------: | -------: | ------- | ------------------------------------ | ------------------ |
| `unified_lead_events_new`     | 26922.2 ⚠️ | 1.41 M | leads   | `tb_bronze_lead_events`          | **26.9 GB** — maior do banco; pipeline de leads |
| `meta_ad_id`                  |  5616.5 ⚠️ | 4.27 M | meta_ads| `tb_bronze_meta_ad_id`           | **5.6 GB** — mapa ad_id↔campanha (granular) |
| `cw_messages_mat`             |  3817.0 ⚠️ | 4.48 M | support | `tb_bronze_chatwoot_messages`    | **3.8 GB** — mensagens Chatwoot (mat.) |
| `cartpanda_physical`          |     655.7 | 512.6 k | cartpanda | `tb_bronze_cartpanda_physical` | lambda/rabbitmq cartpanda |
| `cw_activities_mat`           |     235.8 |  2.39 M | support | `tb_bronze_chatwoot_activities`  | mat. Chatwoot |
| `clickbank_physical_new_aws`  |     213.4 | 332.2 k | clickbank | `tb_bronze_clickbank_physical` | Glue clickbank→mysql (fonte do silver) |
| `cw_conversations_mat`        |      76.5 | 472.1 k | support | `tb_bronze_chatwoot_conversations` | mat. Chatwoot |
| `cw_refund_classifier`        |      22.6 |  23.2 k | support | `tb_bronze_chatwoot_refund_classifier` | classificador de reembolso |
| `google_ad_id`                |      20.5 |  24.2 k | google_ads | `tb_bronze_google_ad_id`      | mapa ad_id Google |
| `call_center_sales`           |       3.0 |   6.7 k | internal | `tb_bronze_call_center_sales`    | vendas call center |
| `digistore_physical`          |       2.3 |   2.3 k | digistore | `tb_bronze_digistore_physical` | feed Digistore |
| `sms_costs`                   |       0.1 |   0.7 k | costs   | `tb_bronze_sms_costs`            | Glue mysql-to-bronze sms_costs |
| `custos_trafego_gestores`     |       0.0 |    52 l | costs   | `tb_bronze_costs_traffic_managers` | base p/ `_daily` |
| `custos_conta_agencia`        |       0.0 |    43 l | costs   | `tb_bronze_costs_agency_account` | base p/ `_daily` |
| `custos_gerais`               |       0.0 |     6 l | costs   | `tb_bronze_costs_general`        | base p/ `_daily` |
| `gross_recovery_target`       |       0.0 |    36 l | leads   | `tb_bronze_gross_recovery_target`| Glue mysql-to-bronze gross_recovery_target |
| `cw_users_mat`                |       0.0 |   104 l | support | `tb_bronze_chatwoot_users`       | mat. Chatwoot |
| `cw_team_members_mat`         |       0.0 |    17 l | support | `tb_bronze_chatwoot_team_members`| mat. Chatwoot |
| `cw_teams_mat`                |       0.0 |     6 l | support | `tb_bronze_chatwoot_teams`       | mat. Chatwoot |

## I) Fontes — dimensões / lookups (pequenas)
| origem | linhas | domínio | **novo_nome** | obs |
|---|---:|---|---|---|
| `buygoods_products` | 2076 | buygoods | `tb_dim_buygoods_product` | par do `dim_clickbank_product` |
| `dim_copywriter` | 74 | internal | `tb_dim_copywriter` | já era dim no nome |
| `clickbank_internal_affiliates` | 22 | clickbank | `tb_dim_clickbank_affiliate` | lookup de afiliado |
| `buygoods_internal_affiliates` | 22 | buygoods | `tb_dim_buygoods_affiliate` ⚠️ | **sem PK** — checar antes |
| `dim_squad` | 18 | internal | `tb_dim_squad` | já era dim no nome |

---
**61 tabelas no total** → **finais (37):** 4 silver · 14 gold · 14 mart · 5 dim · **+ fontes (24):** 19 bronze · 5 dim.
Camadas somadas: **19 bronze · 4 silver · 14 gold · 14 mart · 10 dim**. Fonte da lista: `_mapdata/essenciais.json` → `fonte` (cruzado com `tables.json` p/ tamanhos).

## ⚠️ Decisões a confirmar
1. **`tb_gex_buygoods_unified` → silver** (e não gold): ele é a base unificada que o `gold_buygoods` lê; vem do job do data lake, não de procedure. Faz sentido como silver?
2. **`gerenciador_meta_ads_v2` → silver** (2.3 GB granular): é a base que alimenta `meta_ads_consolidated`/`meta_ads_sales`. Concorda em silver?
3. **`cb_tickets` → `clickbank_tickets`**: assumi `cb` = clickbank. Se for ticket de **atendimento** (Chatwoot), troco para `tb_silver_support_tickets`.
4. **Camada `mart`**: introduzi um 4º nível para as derivadas do gold (era o seu ponto do `channels_marketing`). Se preferir manter só `silver/gold/dim`, eu rebaixo os 11 `mart_*` para `gold_*` (mas perde a distinção de linhagem).
5. **Domínios em inglês**: `atendimento→support`, `reembolso→refund`, `custos→costs`, `gestores→managers`, `canais→channels`, `auditoria→audit`. Confirma essas traduções?
6. **Quem escreve nas fontes (bronze) é externo** — esta é a decisão mais pesada. As 19 tabelas bronze são populadas por **jobs Glue `*-to-mysql`, lambdas (cartpanda/clickbank) e n8n**, não pelas procedures. Migrar de verdade exige **repontar esses produtores** para o `data_team` (senão o bronze no novo banco nasce e congela). Caminhos: **(a)** repontar tudo agora (corte limpo, mas mexe em infra AWS/n8n); **(b)** migrar o dado uma vez e manter os produtores escrevendo no `instituto_experience` por um período (bronze fica desatualizado no `data_team` até virar a chave); **(c)** replicação/CDC temporária. Qual você prefere?
7. **As 3 fontes gigantes (36.3 GB de 36.7)**: `unified_lead_events_new` (26.9 GB), `meta_ad_id` (5.6 GB), `cw_messages_mat` (3.8 GB). Migrar **inteiras** ou com **recorte** (ex.: só N meses / colunas usadas pelas procedures)? Isso decide se o `data_team` nasce com ~44 GB ou bem menor.
8. **`meta_ad_id`/`google_ad_id` como bronze** (e não dim): são mapas ad_id↔campanha, mas **grandes e granulares** (4.27 M / 24 k linhas), então tratei como feed cru. Concorda?
9. **`buygoods_internal_affiliates` sem PK**: única fonte sem chave primária — vale criar PK no destino ou migrar como está?
