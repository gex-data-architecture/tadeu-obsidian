-- ============================================================================
-- DROP DIRETO — instituto_experience
-- Gerado pela skill "limpeza-banco" em 2026-06-03
-- 28 tabelas vazias, sem referência estática, sem escrita (UPDATE_TIME NULL, ~7,7d).
-- Time optou por DROP direto (sem quarentena) — conjunto conhecido e de baixo risco.
-- DROP é IRREVERSÍVEL: o backup do PASSO 0 é OBRIGATÓRIO antes do PASSO 1.
-- Executar com conta privilegiada (DBA). NUNCA rodado pelo MCP (read-only).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PASSO 0 — BACKUP (rodar no SHELL, NÃO no MySQL). Não pule.
-- Gera um .sql que recria + repopula tudo, caso precise voltar atrás.
-- ----------------------------------------------------------------------------
-- mysqldump -h <host> -u <admin> -p \
--   --no-tablespaces --single-transaction \
--   instituto_experience \
--   auth_group auth_group_permissions auth_permission auth_user auth_user_groups \
--   auth_user_user_permissions django_content_type \
--   tbl_teste temp_event_sucess_commited temp_event_sucess_salesbound temp_leads_slicktext \
--   clickbank_affiliate clickbank_affiliate_usd clickbank_nutra_usd \
--   cmp_c01_nov_2024_leads_oneclick fm5d_c01_out_2024_leads leads_cev_c08_jan_202 \
--   abandoned_carts affiliate_products affiliate_details campaign_click customers \
--   historywhatsapp lead_events_target listas_sms_aux sla_alerts_sent \
--   telegram_messages whatsapp_reports \
--   > backup_limpeza_instituto_experience_2026-06-03.sql
--
-- Confira que o arquivo foi gerado e tem tamanho > 0 ANTES de seguir.
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- PASSO 1 — DROP dos nomes originais, ordem FK-safe.
-- (afrouxa a única FK: affiliate_products -> affiliate_details)
-- ----------------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

-- Features de app (filho da FK primeiro)
DROP TABLE IF EXISTS instituto_experience.affiliate_products;   -- filho da FK
DROP TABLE IF EXISTS instituto_experience.affiliate_details;    -- pai da FK
DROP TABLE IF EXISTS instituto_experience.abandoned_carts;
DROP TABLE IF EXISTS instituto_experience.campaign_click;
DROP TABLE IF EXISTS instituto_experience.customers;
DROP TABLE IF EXISTS instituto_experience.historywhatsapp;
DROP TABLE IF EXISTS instituto_experience.lead_events_target;
DROP TABLE IF EXISTS instituto_experience.listas_sms_aux;
DROP TABLE IF EXISTS instituto_experience.sla_alerts_sent;
DROP TABLE IF EXISTS instituto_experience.telegram_messages;
DROP TABLE IF EXISTS instituto_experience.whatsapp_reports;

-- Django / auth (app desativado)
DROP TABLE IF EXISTS instituto_experience.auth_group;
DROP TABLE IF EXISTS instituto_experience.auth_group_permissions;
DROP TABLE IF EXISTS instituto_experience.auth_permission;
DROP TABLE IF EXISTS instituto_experience.auth_user;
DROP TABLE IF EXISTS instituto_experience.auth_user_groups;
DROP TABLE IF EXISTS instituto_experience.auth_user_user_permissions;
DROP TABLE IF EXISTS instituto_experience.django_content_type;

-- Temp / scratch / teste
DROP TABLE IF EXISTS instituto_experience.tbl_teste;
DROP TABLE IF EXISTS instituto_experience.temp_event_sucess_commited;
DROP TABLE IF EXISTS instituto_experience.temp_event_sucess_salesbound;
DROP TABLE IF EXISTS instituto_experience.temp_leads_slicktext;

-- Clickbank affiliate (vazias)
DROP TABLE IF EXISTS instituto_experience.clickbank_affiliate;
DROP TABLE IF EXISTS instituto_experience.clickbank_affiliate_usd;
DROP TABLE IF EXISTS instituto_experience.clickbank_nutra_usd;

-- Exports de campanhas antigas (2024/2025)
DROP TABLE IF EXISTS instituto_experience.cmp_c01_nov_2024_leads_oneclick;
DROP TABLE IF EXISTS instituto_experience.fm5d_c01_out_2024_leads;
DROP TABLE IF EXISTS instituto_experience.leads_cev_c08_jan_202;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- PASSO 2 — Conferência (esperado: 0 linhas).
-- ----------------------------------------------------------------------------
-- SELECT TABLE_NAME FROM information_schema.TABLES
-- WHERE TABLE_SCHEMA='instituto_experience'
--   AND TABLE_NAME IN ('auth_group','auth_group_permissions','auth_permission','auth_user',
--     'auth_user_groups','auth_user_user_permissions','django_content_type','tbl_teste',
--     'temp_event_sucess_commited','temp_event_sucess_salesbound','temp_leads_slicktext',
--     'clickbank_affiliate','clickbank_affiliate_usd','clickbank_nutra_usd',
--     'cmp_c01_nov_2024_leads_oneclick','fm5d_c01_out_2024_leads','leads_cev_c08_jan_202',
--     'abandoned_carts','affiliate_products','affiliate_details','campaign_click','customers',
--     'historywhatsapp','lead_events_target','listas_sms_aux','sla_alerts_sent',
--     'telegram_messages','whatsapp_reports');
