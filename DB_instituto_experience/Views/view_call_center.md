---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 4
tags: [view]
---

# view_call_center

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 4 |

## Lê de
[[general_sales]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`general_sales`.`total_price` AS `total_price`,(`instituto_experience`.`general_sales`.`total_price` * 0.10) AS `imposto`,`instituto_experience`.`general_sales`.`commission` AS `commission`,`instituto_experience`.`general_sales`.`created_at_date` AS `created_at_date` from `instituto_experience`.`general_sales` where (`instituto_experience`.`general_sales`.`linha_receita` = 'Call Center')
```
