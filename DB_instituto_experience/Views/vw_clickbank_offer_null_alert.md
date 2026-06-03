---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 16
tags: [view]
---

# vw_clickbank_offer_null_alert

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 16 |

## Lê de
[[clickbank_physical_new]]

## Lida por
—

## Definição SQL

```sql
select `cb`.`product_name` AS `product_name`,`cb`.`product_sku` AS `product_sku`,`cb`.`sales_type` AS `sales_type`,`cb`.`vendor_name` AS `vendor_name`,count(0) AS `total_transacoes`,sum((case when (`cb`.`payment_status` = 'approved') then 1 else 0 end)) AS `approved`,sum((case when (`cb`.`payment_status` = 'refunded') then 1 else 0 end)) AS `refunded`,sum((case when (`cb`.`payment_status` = 'chargeback') then 1 else 0 end)) AS `chargebacks`,round(coalesce(sum(`cb`.`total_price`),0),2) AS `revenue_brl`,round(coalesce(sum(`cb`.`total_price_usd`),0),2) AS `revenue_usd`,round(coalesce(sum(`cb`.`affiliate_amount`),0),2) AS `affiliate_payout`,count(distinct `cb`.`affiliate_name`) AS `qtd_afiliados`,group_concat(distinct `cb`.`affiliate_name` order by `cb`.`affiliate_name` ASC separator ', ') AS `afiliados`,min(`cb`.`created_at_date`) AS `primeira_venda`,max(`cb`.`created_at_date`) AS `ultima_venda`,(case when (max(`cb`.`created_at_date`) >= (curdate() - interval 7 day)) then 'ATIVO' when (max(`cb`.`created_at_date`) >= (curdate() - interval 30 day)) then 'RECENTE' else 'ANTIGO' end) AS `urgencia` from `instituto_experience`.`clickbank_physical_new` `cb` where ((`cb`.`offer_name` is null) and (`cb`.`payment_status` in ('approved','refunded','chargeback','refunded_partial'))) group by `cb`.`product_name`,`cb`.`product_sku`,`cb`.`sales_type`,`cb`.`vendor_name` order by `revenue_brl` desc
```
