---
tipo: procedure
definer: "diego@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-04-13 00:00:19"
alterada_em: "2026-04-13 00:00:19"
execucoes: ""
tags: [rotina, procedure]
---

# sp_phone_lookup

## Dependências

- **Lê:** [[vw_phone_lookup]]
- **Escreve:** [[numbers_recovered]]
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN
    DECLARE v_phone     VARCHAR(50);
    DECLARE v_full_name VARCHAR(255);

    SELECT phone, full_name
    INTO v_phone, v_full_name
    FROM vw_phone_lookup
    WHERE email = p_email
    LIMIT 1;

    IF v_phone IS NOT NULL THEN
        INSERT IGNORE INTO numbers_recovered
            (unique_key, email, phone, full_name)
        VALUES
            (p_unique_key, p_email, v_phone, v_full_name);
    END IF;
END
```
