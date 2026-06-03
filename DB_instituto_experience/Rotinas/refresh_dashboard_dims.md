---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-13 12:26:22"
alterada_em: "2026-03-13 12:26:22"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_dashboard_dims

## Dependências

- **Lê:** [[dashboard_channels_marketing]], [[dashboard_internal_sales_v2]], [[gerenciador_meta_ads_v2]], [[gerenciador_meta_vendas_v2]]
- **Escreve:** [[dashboard_dim_funil]], [[dashboard_dim_gestor]], [[dashboard_dim_product]], [[dashboard_dim_source]]
- **Cria:** —
- **Trunca:** [[dashboard_dim_funil]], [[dashboard_dim_gestor]], [[dashboard_dim_product]], [[dashboard_dim_source]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 41.5 s |
| Tempo máx | 4m40s |
| Tempo total | 2h5m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 31,666 |

## Corpo SQL

```sql
BEGIN

    TRUNCATE TABLE instituto_experience.dashboard_dim_funil;

    INSERT INTO instituto_experience.dashboard_dim_funil
    SELECT DISTINCT funil_id
    FROM instituto_experience.gerenciador_meta_vendas_v2
    UNION DISTINCT
    SELECT DISTINCT funil_id
    FROM instituto_experience.gerenciador_meta_ads_v2;

    TRUNCATE TABLE instituto_experience.dashboard_dim_gestor;

    INSERT INTO instituto_experience.dashboard_dim_gestor
    SELECT DISTINCT gestor_trafego AS gestor
    FROM instituto_experience.gerenciador_meta_vendas_v2
    UNION DISTINCT
    SELECT DISTINCT gestor_trafego AS gestor
    FROM instituto_experience.gerenciador_meta_ads_v2;
    
	TRUNCATE TABLE instituto_experience.dashboard_dim_product;
    
    INSERT INTO instituto_experience.dashboard_dim_product
    SELECT DISTINCT nome_produto as produto
    FROM instituto_experience.dashboard_channels_marketing;
    
    TRUNCATE TABLE instituto_experience.dashboard_dim_source;
    INSERT INTO instituto_experience.dashboard_dim_source
    SELECT DISTINCT traffic_source as fonte
    FROM instituto_experience.dashboard_internal_sales_v2;

END
```
