---
tipo: incidente
data_deteccao: 2026-06-04
data_inicio: 2026-05-26
severidade: alta
status: aberto
componentes: [meta_ad_id, gerenciador_meta_ads_v2, gerenciador_meta_consolidado_v2]
tags: [incidente, meta-ads, ingestao, dados]
---
# 🔴 Incidente — Investimento (Meta Ads) incompleto desde 26/05

> [!warning] Resumo
> Desde **26/05/2026** a `instituto_experience.meta_ad_id` (bruta de Meta Ads) parou de receber a
> maioria das contas de anúncio: caiu de **~57 contas / ~20.000 ads / ~R$120–150 mil de spend por dia**
> para **3–12 contas / ~200–700 ads / ~R$1–4 mil por dia**. Como `gerenciador_meta_ads_v2` e
> `[[gerenciador_meta_consolidado_v2]]` derivam dela, o **investimento dos dashboards de Meta está subnotificado**
> desde então (e dias **02/06 e 05/06** nem chegaram). **Causa raiz: perda de acesso às contas (token/permissão do Meta).**

## 🎯 Impacto
- **Investimento (spend) subnotificado** em todo o gerenciador Meta a partir de 26/05 → ROI/ROAS/CPA inflados (custo aparece muito menor que o real).
- Dias **02/06** e **05/06** sem spend nenhum.
- Afeta `[[gerenciador_meta_consolidado_v2]]` e qualquer dashboard/análise que use o investimento de Meta.

## 🔎 Investigação (cadeia, de baixo pra cima)
A `[[gerenciador_meta_consolidado_v2]]` está **correta** — o problema é na origem. Provado comparando o spend por dia em cada camada:

| Camada | Veredito |
|---|---|
| `[[gerenciador_meta_consolidado_v2]]` | spend por dia **bate exatamente** com a `ads_v2` → não é aqui |
| `gerenciador_meta_ads_v2` | mesmo penhasco → só reflete a bruta |
| **`[[meta_ad_id]]` (bruta)** | **penhasco em 26/05** → a origem é o problema |
| **Contas ingeridas** | **57 → 3–12 contas em 26/05** 🎯 |

### Evidência — `meta_ad_id` por dia
| Data | Contas | Ads | Spend (BRL) |
|---|--:|--:|--:|
| 23/05 | 58 | 22.740 | — |
| 24/05 | 56 | 19.969 | 149.430 |
| 25/05 | 57 | 20.606 | 117.197 |
| **26/05** | **11** | **210** | **1.195** |
| 27/05 | 12 | 660 | 2.895 |
| 28–31/05 | 8–12 | 434–656 | 1.153–3.214 |
| 01/06 | 6 | 63 | 81 |
| **02/06** | **—** | **0** | **0** (dia ausente) |
| 03/06 | 7 | 421 | 3.659 |
| 04/06 | 3 | 221 | 1.926 |
| **05/06** | **—** | **0** | **0** (dia ausente) |

> A queda é de **contas** (57→poucas), não de volume parcial — assinatura de **token/permissão** que perdeu acesso aos ad accounts.

## 🧩 Causa raiz
**Em 26/05 a integração do Meta perdeu acesso à maioria das contas de anúncio** (provável **token/System User/Business Manager** expirado ou revogado). Só ~3–12 das ~57 contas continuam reportando.

**Pipeline afetado:**
`Meta API → RabbitMQ → lambda instituto-experience-dev-meta_ad_id_rabbitmq (5 min) → meta_ad_id → refresh_gerenciador_meta_ads_v2 → gerenciador_meta_ads_v2 → refresh_gerenciador_meta_consolidado_v2 → gerenciador_meta_consolidado_v2`

> A correção do token está na camada **AWS/Meta** (lambda + produtor da fila / extrator do Meta) — fora do alcance do MCP MySQL (read-only).

## ⚠️ Armadilha de design (atrapalha o conserto)
A `[[refresh_gerenciador_meta_ads_v2]]` **só recalcula os últimos 3 dias** a partir da `meta_ad_id`; **tudo mais antigo que 3 dias é congelado** (copiado da versão anterior). Logo:
- Mesmo após corrigir o token e **rebackfillar** a `meta_ad_id`, a procedure **não recupera sozinha** os dias de 26/05 até ~3 dias atrás — ficam travados errados.
- Só os **últimos 3 dias** se auto-corrigem.

## ✅ Plano de ação
1. **Corrigir o acesso ao Meta** (raiz): renovar/reconectar o token (System User / BM) para as ~57 contas voltarem a fluir para a `meta_ad_id`. Validar via lambda `…meta_ad_id_rabbitmq` / produtor da fila.
2. **Rebackfillar `meta_ad_id`** de **26/05 → hoje** (re-extrair o spend do Meta para o intervalo).
3. **Rebuild do gold (uma vez), pós-backfill** — recomputar `gerenciador_meta_ads_v2` para o intervalo afetado (não só 3 dias) e rodar o consolidado. **DDL = DBA** (o MCP é read-only):
   ```sql
   -- ⚠️ Rodar SÓ depois que a meta_ad_id estiver rebackfillada (26/05 → hoje). DBA.
   TRUNCATE TABLE instituto_experience.gerenciador_meta_ads_v2_stage;

   -- recomputa do bruto TODO o intervalo afetado (mesma agregação da procedure, sem o limite de 3 dias)
   INSERT INTO instituto_experience.gerenciador_meta_ads_v2_stage
   SELECT ma.ad_id, ma.ad_name, ma.created_at_date, ma.account_name, ma.campaign_name, ma.adset_name,
          /* gestor_trafego / funil_id / produto: copiar os mesmos CASE da refresh_gerenciador_meta_ads_v2 */
          ...,
          COALESCE(SUM(ma.amount_spent_brl),0),
          COALESCE(SUM(ma.spent_taxes),0),
          COALESCE(SUM(ma.amount_spent_brl),0)+COALESCE(SUM(ma.spent_taxes),0),
          ROUND((COALESCE(SUM(ma.amount_spent_brl),0)+COALESCE(SUM(ma.spent_taxes),0))/5.2,2),
          SUM(ma.impressions), SUM(ma.reach), SUM(ma.link_clicks)
   FROM instituto_experience.meta_ad_id ma
   WHERE ma.created_at_date >= '2026-05-26'
   GROUP BY ma.ad_id, ma.ad_name, ma.created_at_date, ma.account_name, ma.campaign_name, ma.adset_name;

   -- mantém o histórico bom (< 26/05) da tabela atual
   INSERT INTO instituto_experience.gerenciador_meta_ads_v2_stage
   SELECT * FROM instituto_experience.gerenciador_meta_ads_v2
   WHERE created_at_date < '2026-05-26';

   -- swap atômico
   RENAME TABLE
     instituto_experience.gerenciador_meta_ads_v2       TO instituto_experience.gerenciador_meta_ads_v2_old,
     instituto_experience.gerenciador_meta_ads_v2_stage TO instituto_experience.gerenciador_meta_ads_v2,
     instituto_experience.gerenciador_meta_ads_v2_old   TO instituto_experience.gerenciador_meta_ads_v2_stage;

   CALL instituto_experience.refresh_gerenciador_meta_consolidado_v2();
   ```
4. **Validar:** spend diário de 26/05→hoje volta ao patamar de ~R$120–150 mil e contas ~57.

## 🛡️ Prevenção (melhorias sugeridas)
- **Alerta de cobertura:** monitorar nº de contas/spend diário do Meta; disparar se cair > X% vs média (pegaria isso no dia 26/05).
- **Alerta de expiração de token** do Meta (System User tokens expiram).
- **Repensar o "congela após 3 dias"** da `refresh_gerenciador_meta_ads_v2`: aumentar a janela de recompute, ou recomputar do bruto sob demanda quando houver backfill — para que gaps não virem permanentes.

## 🔗 Relacionados
- Objetos: [[meta_ad_id]] · [[gerenciador_meta_ads_v2]] · [[gerenciador_meta_consolidado_v2]] · [[refresh_gerenciador_meta_ads_v2]] · [[refresh_gerenciador_meta_consolidado_v2]]
- Schema: [[CLAUDE]] · Diário: [[log]]
