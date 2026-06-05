---
tipo: decisao
status: aceita
data: 2026-06-02
tags: [decisao, evento, manutencao]
---
# Desabilitar `evt_refresh_dashboard_affiliate_nutra` e `_usd`

## Contexto
Existiam dois eventos rodando a cada **10 min** que só faziam `CALL` das procedures
`refresh_dashboard_affiliate_nutra()` e `refresh_dashboard_affiliate_nutra_usd()`.
Verificado via MCP (`information_schema.ROUTINES`) que essas duas procedures **já são chamadas**
por `[[sp_master_run_all]]` — e ele é a **única** rotina do banco que as referencia.
O `[[sp_master_run_all]]` é disparado pelo evento `[[ev_master_dashboard_refresh]]` a cada **60 min**.

## Decisão
**Desabilitar** (não dropar) os dois eventos:
```sql
ALTER EVENT instituto_experience.evt_refresh_dashboard_affiliate_nutra DISABLE;
ALTER EVENT instituto_experience.evt_refresh_dashboard_affiliate_nutra_usd DISABLE;
```
Executado pelo time em 2026-06-02. Status confirmado via MCP: ambos `DISABLED`.

## Consequências
- ✅ Remove redundância (os dashboards continuam sendo gerados pelo `sp_master_run_all`).
- ⚠️ **Trade-off aceito:** a atualização dos dashboards *affiliate nutra* (BRL e USD) passa de
  **10 min → 60 min** (cadência do master). Se precisar voltar à frequência alta, basta
  `ALTER EVENT ... ENABLE` — nada foi dropado.
- Mantidos os eventos para reversão fácil; não há perda de objeto.

## Relacionados
[[evt_refresh_dashboard_affiliate_nutra]] · [[evt_refresh_dashboard_affiliate_nutra_usd]] ·
[[refresh_dashboard_affiliate_nutra]] · [[refresh_dashboard_affiliate_nutra_usd]] ·
[[sp_master_run_all]] · [[ev_master_dashboard_refresh]]
