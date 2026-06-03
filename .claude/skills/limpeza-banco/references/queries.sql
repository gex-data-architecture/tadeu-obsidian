-- ============================================================================
-- queries.sql — blocos prontos para a skill "limpeza-banco"
-- Substitua {{SCHEMA}} pelo schema-alvo (padrão: instituto_experience).
-- O MCP roda UMA instrução por chamada — não envie várias separadas por ';'.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- PASSO 1 — Candidatas brutas: vazias (estimativa), não _stage/_old, e sem
-- referência estática em procedure/function, event ou view.
-- (substring LIKE é conservador de propósito: na dúvida, marca como usada)
-- ----------------------------------------------------------------------------
SELECT t.TABLE_NAME, t.TABLE_ROWS AS est_rows, ROUND(t.DATA_LENGTH/1024/1024,2) AS mb
FROM information_schema.TABLES t
WHERE t.TABLE_SCHEMA='{{SCHEMA}}'
  AND t.TABLE_TYPE='BASE TABLE'
  AND t.TABLE_ROWS=0
  AND t.TABLE_NAME NOT LIKE '%\_stage'
  AND t.TABLE_NAME NOT LIKE '%\_old'
  AND t.TABLE_NAME NOT LIKE '%\_new'   -- inclui _aws_new (alvo de swap)
  AND NOT EXISTS (SELECT 1 FROM information_schema.ROUTINES r
        WHERE r.ROUTINE_SCHEMA='{{SCHEMA}}' AND r.ROUTINE_DEFINITION LIKE CONCAT('%', t.TABLE_NAME, '%'))
  AND NOT EXISTS (SELECT 1 FROM information_schema.EVENTS e
        WHERE e.EVENT_SCHEMA='{{SCHEMA}}' AND e.EVENT_DEFINITION LIKE CONCAT('%', t.TABLE_NAME, '%'))
  AND NOT EXISTS (SELECT 1 FROM information_schema.VIEWS v
        WHERE v.TABLE_SCHEMA='{{SCHEMA}}' AND v.VIEW_DEFINITION LIKE CONCAT('%', t.TABLE_NAME, '%'))
ORDER BY t.TABLE_NAME;


-- ----------------------------------------------------------------------------
-- PASSO 1b — TESTE DO IRMÃO VIVO. O filtro de sufixo não pega tudo: o alvo de um
-- swap pode se chamar X_aws_new, X_v2, etc. Para cada candidata, procure irmãs
-- com o mesmo prefixo-base que estejam CHEIAS ou escritas recentemente. Se houver,
-- a candidata vazia é alvo de swap → DESCARTE. (Ajuste o prefixo-base à mão.)
-- Ex.: candidata gold_clickbank_aws_new → base 'gold_clickbank'.
-- ----------------------------------------------------------------------------
SELECT TABLE_NAME, TABLE_ROWS AS est_rows, ROUND(DATA_LENGTH/1024/1024,2) AS mb,
       CREATE_TIME, UPDATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='{{SCHEMA}}'
  AND TABLE_NAME LIKE '<prefixo_base>%'   -- ex.: 'gold_clickbank%'
ORDER BY TABLE_NAME;
-- Leitura: se a candidata vazia tem irmã com muitos rows / UPDATE_TIME de hoje,
-- ela é o alvo do próximo swap. Mantém.


-- ----------------------------------------------------------------------------
-- PASSO 2 — Confirmar vazio DE VERDADE. Gere dinamicamente um UNION ALL com as
-- candidatas do passo 1. Só seguem as que derem 0. Modelo:
-- ----------------------------------------------------------------------------
SELECT '<tabela_1>' t, COUNT(*) c FROM {{SCHEMA}}.<tabela_1>
UNION ALL SELECT '<tabela_2>', COUNT(*) FROM {{SCHEMA}}.<tabela_2>
-- ... uma linha por candidata ...
;


-- ----------------------------------------------------------------------------
-- PASSO 3a — FKs apontando PARA as candidatas (preencha o IN com a lista).
-- Resultado vazio = nenhuma dependência de FK. FK interna ao grupo => ordem.
-- ----------------------------------------------------------------------------
SELECT TABLE_NAME AS filho, REFERENCED_TABLE_NAME AS pai_candidato, CONSTRAINT_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA='{{SCHEMA}}'
  AND REFERENCED_TABLE_NAME IN ( /* 'cand1','cand2',... */ );


-- ----------------------------------------------------------------------------
-- PASSO 3b — Triggers nas candidatas.
-- ----------------------------------------------------------------------------
SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE AS na_tabela
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA='{{SCHEMA}}'
  AND EVENT_OBJECT_TABLE IN ( /* 'cand1','cand2',... */ );


-- ----------------------------------------------------------------------------
-- PASSO 4a — Uptime (tamanho da janela dos contadores / UPDATE_TIME).
-- ----------------------------------------------------------------------------
SHOW GLOBAL STATUS LIKE 'Uptime';


-- ----------------------------------------------------------------------------
-- PASSO 4b — Escrita recente e data de criação das candidatas.
-- UPDATE_TIME NULL = sem DML desde o restart. CREATE_TIME recente = bandeira vermelha.
-- ----------------------------------------------------------------------------
SELECT TABLE_NAME, UPDATE_TIME AS ultima_escrita, CREATE_TIME AS criada_em
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='{{SCHEMA}}'
  AND TABLE_NAME IN ( /* 'cand1','cand2',... */ )
ORDER BY UPDATE_TIME DESC, TABLE_NAME;


-- ----------------------------------------------------------------------------
-- PASSO 5 — Leitura real (precisa de SELECT em performance_schema).
-- Se vier "SELECT command denied", caia para a quarentena por RENAME e peça o GRANT.
-- LEFT JOIN para mostrar TODAS as candidatas, mesmo as nunca tocadas (0/NULL).
-- ----------------------------------------------------------------------------
SELECT c.tabela, io.COUNT_READ AS leituras, io.COUNT_FETCH AS fetch_rows,
       io.COUNT_WRITE AS escritas, io.COUNT_INSERT AS inserts,
       io.COUNT_UPDATE AS updates, io.COUNT_DELETE AS deletes
FROM ( SELECT '<tabela_1>' tabela UNION ALL SELECT '<tabela_2>' /* ... */ ) c
LEFT JOIN performance_schema.table_io_waits_summary_by_table io
       ON io.OBJECT_SCHEMA='{{SCHEMA}}' AND io.OBJECT_NAME=c.tabela
ORDER BY io.COUNT_READ DESC, io.COUNT_WRITE DESC, c.tabela;


-- ----------------------------------------------------------------------------
-- VIEWS — passo 1: views não referenciadas por procedure/event/outra view.
-- ----------------------------------------------------------------------------
SELECT v.TABLE_NAME AS view_name
FROM information_schema.VIEWS v
WHERE v.TABLE_SCHEMA='{{SCHEMA}}'
  AND NOT EXISTS (SELECT 1 FROM information_schema.ROUTINES r
        WHERE r.ROUTINE_SCHEMA='{{SCHEMA}}' AND r.ROUTINE_DEFINITION LIKE CONCAT('%', v.TABLE_NAME, '%'))
  AND NOT EXISTS (SELECT 1 FROM information_schema.EVENTS e
        WHERE e.EVENT_SCHEMA='{{SCHEMA}}' AND e.EVENT_DEFINITION LIKE CONCAT('%', v.TABLE_NAME, '%'))
  AND NOT EXISTS (SELECT 1 FROM information_schema.VIEWS v2
        WHERE v2.TABLE_SCHEMA='{{SCHEMA}}' AND v2.TABLE_NAME<>v.TABLE_NAME
          AND v2.VIEW_DEFINITION LIKE CONCAT('%', v.TABLE_NAME, '%'))
ORDER BY v.TABLE_NAME;

-- VIEWS — passo 2: para CADA view do passo 1, teste se está quebrada.
-- Erro = candidata (referencia objeto inexistente). Sucesso = NÃO é candidata.
-- Rode uma por vez:
SELECT * FROM {{SCHEMA}}.<view> LIMIT 0;


-- ============================================================================
-- GRANT (entregar ao DBA para liberar a checagem de leitura do PASSO 5).
-- Quem executa é o DBA com a conta master. Ajuste o host do usuário do MCP.
-- ============================================================================
-- GRANT SELECT ON performance_schema.table_io_waits_summary_by_table    TO '<user_mcp>'@'%';
-- GRANT SELECT ON performance_schema.events_statements_summary_by_digest TO '<user_mcp>'@'%';
-- (ou, mais simples e ainda só leitura:)
-- GRANT SELECT ON performance_schema.* TO '<user_mcp>'@'%';
