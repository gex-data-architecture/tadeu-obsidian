---
tipo: procedure
definer: "gabriel_gomes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2025-11-18 03:28:59"
alterada_em: "2025-11-18 03:28:59"
execucoes: ""
tags: [rotina, procedure]
---

# refresh_internal_sales

## Dependências

- **Lê:** [[internal_sales]]
- **Escreve:** [[internal_sales_mat]], [[internal_sales_refresh_log]]
- **Cria:** —
- **Trunca:** [[internal_sales_mat]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN
    DECLARE start_time DATETIME;
    DECLARE end_time DATETIME;
    DECLARE row_count INT;
    DECLARE duration INT;

    SET start_time = NOW();

    TRUNCATE TABLE internal_sales_mat;

    INSERT INTO internal_sales_mat
    SELECT * FROM internal_sales;

    SET row_count = ROW_COUNT();

    SET end_time = NOW();
    SET duration = TIMESTAMPDIFF(SECOND, start_time, end_time);

    INSERT INTO internal_sales_refresh_log
    (refreshed_at, records_count, duration_seconds, start_time, end_time)
    VALUES
        (NOW(), row_count, duration, start_time, end_time);

END
```
