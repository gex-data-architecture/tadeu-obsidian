---
tipo: view
definer: "gabriel_gomes@%"
security_type: "DEFINER"
colunas: 12
tags: [view]
---

# vw_affiliate_ads_spy

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | gabriel_gomes@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 12 |

## Lê de
[[cartpanda_physical]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`cartpanda_physical`.`created_at_date` AS `created_at_date`,nullif(lower(regexp_replace(trim((case when (`instituto_experience`.`cartpanda_physical`.`product_name` like '%-%') then trim(substring_index(`instituto_experience`.`cartpanda_physical`.`product_name`,'-',1)) when regexp_like(`instituto_experience`.`cartpanda_physical`.`product_name`,'[0-9]') then trim(regexp_substr(`instituto_experience`.`cartpanda_physical`.`product_name`,'^[^0-9]+')) else `instituto_experience`.`cartpanda_physical`.`product_name` end)),'[^a-zA-Z0-9]','')),'') AS `product_name`,nullif(`instituto_experience`.`cartpanda_physical`.`affiliate_name`,'') AS `affiliate_name`,nullif(substring_index(substring_index(replace(replace(`instituto_experience`.`cartpanda_physical`.`referring_site`,'https://',''),'http://',''),'/',1),'?',1),'') AS `referring_site`,nullif(`instituto_experience`.`cartpanda_physical`.`utm_source`,'') AS `utm_source`,nullif(`instituto_experience`.`cartpanda_physical`.`utm_medium`,'') AS `utm_medium`,nullif(`instituto_experience`.`cartpanda_physical`.`utm_campaign`,'') AS `utm_campaign`,nullif(`instituto_experience`.`cartpanda_physical`.`utm_content`,'') AS `utm_content`,nullif(`instituto_experience`.`cartpanda_physical`.`utm_term`,'') AS `src`,nullif(`instituto_experience`.`cartpanda_physical`.`src`,'') AS `utm_term`,count(0) AS `total_transactions`,(sum(`instituto_experience`.`cartpanda_physical`.`total_price`) / 5.4) AS `total_revenue_usd` from `instituto_experience`.`cartpanda_physical` where ((`instituto_experience`.`cartpanda_physical`.`created_at_date` >= (curdate() - interval 3 month)) and (`instituto_experience`.`cartpanda_physical`.`affiliate_name` is not null) and (`instituto_experience`.`cartpanda_physical`.`affiliate_name` <> '')) group by `instituto_experience`.`cartpanda_physical`.`created_at_date`,lower(regexp_replace(trim((case when (`instituto_experience`.`cartpanda_physical`.`product_name` like '%-%') then trim(substring_index(`instituto_experience`.`cartpanda_physical`.`product_name`,'-',1)) when regexp_like(`instituto_experience`.`cartpanda_physical`.`product_name`,'[0-9]') then trim(regexp_substr(`instituto_experience`.`cartpanda_physical`.`product_name`,'^[^0-9]+')) else `instituto_experience`.`cartpanda_physical`.`product_name` end)),'[^a-zA-Z0-9]','')),`instituto_experience`.`cartpanda_physical`.`affiliate_name`,substring_index(substring_index(replace(replace(`instituto_experience`.`cartpanda_physical`.`referring_site`,'https://',''),'http://',''),'/',1),'?',1),`instituto_experience`.`cartpanda_physical`.`utm_source`,`instituto_experience`.`cartpanda_physical`.`utm_medium`,`instituto_experience`.`cartpanda_physical`.`utm_campaign`,`instituto_experience`.`cartpanda_physical`.`utm_content`,`instituto_experience`.`cartpanda_physical`.`utm_term`,`instituto_experience`.`cartpanda_physical`.`src` order by `instituto_experience`.`cartpanda_physical`.`created_at_date` desc,`total_revenue_usd` desc
```
