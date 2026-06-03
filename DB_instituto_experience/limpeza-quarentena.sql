-- ============================================================================
-- QUARENTENA POR RENAME — instituto_experience  (LOTE 2)
-- Gerado pela skill "limpeza-banco" em 2026-06-03
-- 5 tabelas dashboard_*/gold/v2 vazias, sem referência estática, sem escrita.
--
-- POR QUE QUARENTENA (e não DROP direto como o lote 1):
--   São tabelas de DASHBOARD/GOLD que provavelmente alimentam Looker Studio.
--   A LEITURA externa NÃO é confirmável por SQL (sem performance_schema), e o
--   risco aqui é maior que o do lote 1. Então: NÃO dropar ainda.
--   Renomear para _zzdrop_ e observar 1–2 semanas. Se algo quebrar, é porque
--   alguém lia a tabela: RENAME de volta (instrução no fim).
--
-- Executar com conta privilegiada (DBA). NUNCA rodado pelo MCP (read-only).
-- ============================================================================

-- Conferido em 2026-06-03 para as 5 abaixo:
--   COUNT(*)=0 real | sem sufixo de swap (_stage/_old/_aws_new) e sem irmão vivo
--   | sem ref. em procedure/function/event/view | sem FK apontando | sem trigger
--   | UPDATE_TIME NULL (sem DML desde o último restart).
-- Única incógnita: leitura externa (Looker/n8n) — é o que a quarentena testa.

-- ----------------------------------------------------------------------------
-- ATENÇÃO — fora deste lote (descoberto na análise, NÃO mexer):
--   clickbank_physical_new_aws_new, gold_clickbank_aws_new e
--   dashboard_channels_marketing_aws_new são ALVOS DE SWAP (_aws_new), irmãos
--   das tabelas vivas clickbank_physical_new_aws (330k), gold_clickbank_aws
--   (216k) e dashboard_channels_marketing_aws (47k). Vazias só ENTRE ciclos.
--   Mesma armadilha de _stage/_old. JAMAIS entram em limpeza.
-- ----------------------------------------------------------------------------

SET FOREIGN_KEY_CHECKS = 0;  -- nenhuma FK conhecida nestas, mas mantém o padrão seguro

RENAME TABLE instituto_experience.clickbank_physical_v2           TO instituto_experience._zzdrop_clickbank_physical_v2;
RENAME TABLE instituto_experience.dashboard_cartpanda_pais_diario TO instituto_experience._zzdrop_dashboard_cartpanda_pais_diario;
RENAME TABLE instituto_experience.dashboard_dim_gestorl          TO instituto_experience._zzdrop_dashboard_dim_gestorl;
RENAME TABLE instituto_experience.dashboard_gerenciador_unificado TO instituto_experience._zzdrop_dashboard_gerenciador_unificado;
RENAME TABLE instituto_experience.dashboard_partner_affiliates    TO instituto_experience._zzdrop_dashboard_partner_affiliates;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- OBSERVAÇÃO — janela de 1–2 semanas (até ~2026-06-17).
-- Quebrou um dashboard/relatório? Era lido. Reverta a tabela específica:
--   RENAME TABLE instituto_experience._zzdrop_dashboard_dim_gestorl
--                TO instituto_experience.dashboard_dim_gestorl;
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- DROP FINAL (só depois da janela sem reclamação). Backup mysqldump antes!
-- mysqldump -h <host> -u <admin> -p --no-tablespaces --single-transaction \
--   instituto_experience \
--   _zzdrop_clickbank_physical_v2 _zzdrop_dashboard_cartpanda_pais_diario \
--   _zzdrop_dashboard_dim_gestorl _zzdrop_dashboard_gerenciador_unificado \
--   _zzdrop_dashboard_partner_affiliates \
--   > backup_quarentena_lote2_instituto_experience_2026-06-17.sql
--
-- DROP TABLE IF EXISTS instituto_experience._zzdrop_clickbank_physical_v2;
-- DROP TABLE IF EXISTS instituto_experience._zzdrop_dashboard_cartpanda_pais_diario;
-- DROP TABLE IF EXISTS instituto_experience._zzdrop_dashboard_dim_gestorl;
-- DROP TABLE IF EXISTS instituto_experience._zzdrop_dashboard_gerenciador_unificado;
-- DROP TABLE IF EXISTS instituto_experience._zzdrop_dashboard_partner_affiliates;
-- ============================================================================
