---
tipo: procedure
definer: "diego@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-04-08 02:33:13"
alterada_em: "2026-04-08 02:33:13"
execucoes: ""
tags: [rotina, procedure]
---

# sp_enrich_phone_from_email

## Dependências

- **Lê:** [[unified_lead_events_new]]
- **Escreve:** [[unified_lead_events_new]]
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
    DECLARE v_found_phone VARCHAR(50) DEFAULT NULL;

    IF LOWER(p_platform) = 'clickbank' THEN

        SELECT client_phone
        INTO   v_found_phone
        FROM   unified_lead_events_new
        WHERE  LOWER(client_email) = LOWER(p_email)
          AND  client_phone IS NOT NULL
          AND  client_phone <> ''
        ORDER BY created_at DESC
        LIMIT 1;

        IF v_found_phone IS NOT NULL THEN
            UPDATE unified_lead_events_new
            SET    client_phone = v_found_phone
            WHERE  unique_key   = p_unique_key
              AND (client_phone IS NULL OR client_phone = '');
        END IF;

    END IF;

END
```
