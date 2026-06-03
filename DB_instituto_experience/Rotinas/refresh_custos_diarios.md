---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-13 10:57:33"
alterada_em: "2026-03-13 10:57:33"
execucoes: ""
tags: [rotina, procedure]
---

# refresh_custos_diarios

## Dependências

- **Lê:** [[custos_conta_agencia]], [[custos_trafego_gestores]]
- **Escreve:** [[custos_conta_agencia_diaria]], [[custos_trafego_gestores_diaria]]
- **Cria:** —
- **Trunca:** [[custos_conta_agencia_diaria]], [[custos_trafego_gestores_diaria]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

  -- ── Trafego Gestores ──────────────────────────────────────
  TRUNCATE TABLE instituto_experience.custos_trafego_gestores_diaria;

  INSERT INTO instituto_experience.custos_trafego_gestores_diaria
    (data, fonte, funil_id, produto, gestor, conta, custo_brl, custos_gerais, status)
  WITH RECURSIVE dias AS (
    SELECT 0 AS offset_dia
    UNION ALL
    SELECT offset_dia + 1 FROM dias WHERE offset_dia < 6
  )
  SELECT
    DATE_ADD(c.data_inicio, INTERVAL d.offset_dia DAY) AS data,
    c.fonte,
    c.funil_id,
    c.produto,
    c.gestor,
    c.conta,
    ROUND(c.custo_brl     / 7, 2) AS custo_brl,
    ROUND(c.custos_gerais / 7, 2) AS custos_gerais,
    c.status
  FROM instituto_experience.custos_trafego_gestores c
  CROSS JOIN dias d
  WHERE c.is_current = 1;

  -- ── Contas Agência ────────────────────────────────────────
  TRUNCATE TABLE instituto_experience.custos_conta_agencia_diaria;

  INSERT INTO instituto_experience.custos_conta_agencia_diaria
    (data, fonte, agencia, funil_id, produto, gestor, taxa, custo, custo_real, status)
  WITH RECURSIVE dias AS (
    SELECT 0 AS offset_dia
    UNION ALL
    SELECT offset_dia + 1 FROM dias WHERE offset_dia < 6
  )
  SELECT
    DATE_ADD(c.data_inicio, INTERVAL d.offset_dia DAY) AS data,
    c.fonte,
    c.agencia,
    c.funil_id,
    c.produto,
    c.gestor,
    c.taxa,
    ROUND(c.custo      / 7, 2) AS custo,
    ROUND(c.custo_real / 7, 2) AS custo_real,
    c.status
  FROM instituto_experience.custos_conta_agencia c
  CROSS JOIN dias d
  WHERE c.is_current = 1;

END
```
