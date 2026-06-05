---
tipo: view
definer: "diego@%"
security_type: "DEFINER"
colunas: 5
tags: [view]
---

# vw_logicall_rpl

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | diego@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 5 |

## Lê de
[[vw_logicall_leads]]

## Lida por
—

## Definição SQL

```sql
select `s`.`data` AS `data`,`s`.`nome_produto` AS `nome_produto`,sum(`s`.`logicall_usd`) AS `revenue`,sum(`instituto_experience`.`l`.`leads_logicall`) AS `leads`,(sum(`s`.`logicall_usd`) / nullif(sum(`instituto_experience`.`l`.`leads_logicall`),0)) AS `rpl` from (`instituto_experience`.`call_center_sales` `s` left join `instituto_experience`.`vw_logicall_leads` `l` on(((`s`.`data` = `instituto_experience`.`l`.`data`) and (`s`.`nome_produto` = `instituto_experience`.`l`.`nome_produto`)))) where (`s`.`logicall_usd` > 0) group by `s`.`data`,`s`.`nome_produto`
```
