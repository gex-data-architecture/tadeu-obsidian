---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 3
tags: [view]
---

# nps_distribuicao

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 3 |

## Lê de
[[nps_affiliate_groups]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`nps_affiliate_groups`.`support_note` AS `nota`,(convert('Suporte' using utf8mb4) collate utf8mb4_unicode_ci) AS `setor`,count(0) AS `votos` from `instituto_experience`.`nps_affiliate_groups` where (`instituto_experience`.`nps_affiliate_groups`.`support_note` is not null) group by `instituto_experience`.`nps_affiliate_groups`.`support_note` union all select `instituto_experience`.`nps_affiliate_groups`.`infrastructure_note` AS `infrastructure_note`,(convert('Infra' using utf8mb4) collate utf8mb4_unicode_ci) AS `CONVERT('Infra' USING utf8mb4) COLLATE utf8mb4_unicode_ci`,count(0) AS `COUNT(*)` from `instituto_experience`.`nps_affiliate_groups` where (`instituto_experience`.`nps_affiliate_groups`.`infrastructure_note` is not null) group by `instituto_experience`.`nps_affiliate_groups`.`infrastructure_note` union all select `instituto_experience`.`nps_affiliate_groups`.`copywriting_note` AS `copywriting_note`,(convert('Copy' using utf8mb4) collate utf8mb4_unicode_ci) AS `CONVERT('Copy' USING utf8mb4) COLLATE utf8mb4_unicode_ci`,count(0) AS `COUNT(*)` from `instituto_experience`.`nps_affiliate_groups` where (`instituto_experience`.`nps_affiliate_groups`.`copywriting_note` is not null) group by `instituto_experience`.`nps_affiliate_groups`.`copywriting_note` union all select `instituto_experience`.`nps_affiliate_groups`.`gex_note` AS `gex_note`,(convert('GEX' using utf8mb4) collate utf8mb4_unicode_ci) AS `CONVERT('GEX' USING utf8mb4) COLLATE utf8mb4_unicode_ci`,count(0) AS `COUNT(*)` from `instituto_experience`.`nps_affiliate_groups` where (`instituto_experience`.`nps_affiliate_groups`.`gex_note` is not null) group by `instituto_experience`.`nps_affiliate_groups`.`gex_note`
```
