---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-02-16 17:35:23"
alterada_em: "2026-02-16 17:35:23"
execucoes: ""
tags: [rotina, procedure]
---

# sp_refresh_gerenciador_meta_vendas

## Dependências

- **Lê:** [[cartpanda_physical]]
- **Escreve:** [[gerenciador_meta_vendas]]
- **Cria:** —
- **Trunca:** [[gerenciador_meta_vendas]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

    TRUNCATE TABLE `instituto_experience`.`gerenciador_meta_vendas`;

    INSERT INTO `instituto_experience`.`gerenciador_meta_vendas` (
        utm_content,
        created_at_date,
        gestor_trafego,
        funil_id,
        total_transactions,
        total_price,
        commission,
        taxes,
        total_refund,
        product_cost,
        imposto
    )
    SELECT
        cp.utm_content,
        cp.created_at_date,
        CASE
            WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%'
                THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
            WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%'
                THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
            ELSE 'Não Encontrado'
            END AS gestor_trafego,
        CASE
            WHEN cp.offer_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT('Funil de Nova Ideia #',
                            REGEXP_SUBSTR(
                                    SUBSTRING_INDEX(cp.offer_name, 'Funil de Nova Ideia #', -1),
                                    '^[0-9]+'
                            ))
            ELSE 'Não Encontrado'
            END AS funil_id,
        COUNT(DISTINCT cp.transaction_id) AS total_transactions,
        SUM(cp.total_price) AS total_price,
        SUM(cp.commission) AS commission,
        SUM(cp.taxes) AS taxes,
        SUM(cp.total_refund) AS total_refund,
        SUM(cp.product_cost) AS product_cost,
        SUM(cp.total_price * 0.03) AS imposto
    FROM `instituto_experience`.`cartpanda_physical` cp FORCE INDEX (`idx_cp_created_date`)
    WHERE cp.created_at_date >= '2026-01-01'
      AND (cp.affiliate_name IS NULL OR cp.affiliate_name = '')
      AND cp.client_email NOT LIKE '%institutoexperience%'
      AND cp.offer_name LIKE '%Nova Ideia%'
      AND cp.offer_name NOT LIKE '%Thales Pater%'
      AND LOWER(cp.offer_name) NOT LIKE '%affiliate marketing%'
      AND cp.utm_content IS NOT NULL
      AND cp.utm_content != ''
    GROUP BY
        cp.utm_content,
        cp.created_at_date,
        gestor_trafego,
        funil_id;

END
```
