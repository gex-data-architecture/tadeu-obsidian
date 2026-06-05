---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-02-10 21:27:57"
alterada_em: "2026-02-10 21:27:57"
execucoes: ""
tags: [rotina, procedure]
---

# kill_metadata_locks

## Dependências

- **Lê:** —
- **Escreve:** —
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
    DECLARE done INT DEFAULT FALSE;
    DECLARE process_id BIGINT;
    DECLARE cur CURSOR FOR 
        SELECT ID 
        FROM information_schema.PROCESSLIST 
        WHERE STATE LIKE '%metadata lock%' 
           OR STATE LIKE '%Waiting for table%'
           AND TIME > 60; -- processos com mais de 60 segundos
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO process_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Construir e executar KILL
        SET @kill_stmt = CONCAT('KILL ', process_id);
        PREPARE stmt FROM @kill_stmt;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
        SELECT CONCAT('Processo ', process_id, ' terminado.') AS Mensagem;
    END LOOP;
    
    CLOSE cur;
END
```
