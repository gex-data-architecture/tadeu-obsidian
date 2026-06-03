---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-06-01 21:50:49"
alterada_em: "2026-06-01 21:50:49"
execucoes: 40
tags: [rotina, procedure]
---

# fix_gestor_offer_names_aws

## Dependências

- **Lê:** [[buygoods_internal_affiliates]]
- **Escreve:** [[tb_gex_buygoods_unified]]
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 40 |
| Tempo médio | 15.2 s |
| Tempo máx | 18.9 s |
| Tempo total | 10m6s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
BEGIN

    SET SQL_SAFE_UPDATES = 0;

    UPDATE instituto_experience.tb_gex_buygoods_unified cb
        INNER JOIN instituto_experience.buygoods_internal_affiliates ia
            ON ia.affiliate_name = cb.affiliate_name
    SET cb.offer_name = CASE
                            WHEN LOCATE('] [', cb.offer_name) > 0 THEN
                                CONCAT(
                                    SUBSTRING(
                                        cb.offer_name, 1,
                                        CHAR_LENGTH(cb.offer_name)
                                            - CHAR_LENGTH(SUBSTRING_INDEX(cb.offer_name, '] [', -1))
                                            - 3
                                    ),
                                    '] [Gestor de Tráfego: ', ia.traffic_manager, '] [',
                                    SUBSTRING_INDEX(cb.offer_name, '] [', -1)
                                )
                            ELSE CONCAT(cb.offer_name, ' [Gestor de Tráfego: ', ia.traffic_manager, ']')
                        END,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.is_house_traffic = 1
      AND cb.offer_name NOT LIKE '%Gestor de Tráfego:%'
      AND cb.offer_name IS NOT NULL;

    SET SQL_SAFE_UPDATES = 1;

END
```
