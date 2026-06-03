---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-09 19:40:51"
alterada_em: "2026-03-09 19:40:51"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_dashboard_leads_por_dia

## Dependências

- **Lê:** [[unified_lead_events_new]]
- **Escreve:** [[dashboard_leads_por_dia]]
- **Cria:** —
- **Trunca:** [[dashboard_leads_por_dia]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 5.9 s |
| Tempo máx | 22.6 s |
| Tempo total | 17m53s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 27,311 |

## Corpo SQL

```sql
BEGIN
    TRUNCATE TABLE instituto_experience.dashboard_leads_por_dia;

    INSERT INTO instituto_experience.dashboard_leads_por_dia
    SELECT
        order_date,
        COUNT(DISTINCT client_email) AS total_leads,
        COUNT(DISTINCT CASE
            WHEN data_insercao_activecampaign IS NOT NULL
            THEN client_email
        END) AS leads_com_data_email
    FROM instituto_experience.unified_lead_events_new
    WHERE event_type IN ('lost_cart', 'lost_cart_fast', 'purchase_approved')
      AND order_date >= '2026-01-01'
    GROUP BY order_date
    ORDER BY order_date DESC;

END
```
