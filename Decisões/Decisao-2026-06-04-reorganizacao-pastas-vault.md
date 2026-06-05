---
tipo: decisao
tags: [decisao, adr, conhecimento, vault, organizacao]
numero: ADR-001
status: aceito
data: 2026-06-04
autores: [Tadeu]
supera: null
superado_por: null
---
# ADR-001 — Reorganização da arquitetura de pastas do vault

> [!info] Status
> **`aceito`** · 2026-06-04 · Tadeu — **executado** (migração feita com `git mv`).
> Origem: call com o CTO (Gabriel) em 04/06 sobre estrutura/governança do Obsidian.

## Contexto
O vault do time de dados cresceu com pastas soltas na raiz e **duas raízes de banco**
(`DB_instituto_experience` e `DB_data_team`) de mesma natureza. Na call, o CTO apontou que a
estrutura está "muito centralizada/desorganizada" e sugeriu princípios de governança de
conhecimento (separar sistema de conhecimento, camada de inputs crus reprocessáveis,
unificar pastas de mesma natureza, agrupar por competência, não criar pasta vazia). O
objetivo final é deixar o conhecimento **estruturado e fácil de navegar** — e acelerar o
onboarding de novas fontes/gateways.

## Decisão (proposta)
**Reorganizar o vault em pastas-mãe por domínio: separar o `Sistema` (máquina) do conteúdo,
**dissolver o balde genérico "Conhecimento"** (cada nota vai para a entidade dona — "casa = dono"),
unificar os dois bancos em `Banco de Dados/<engine>/<db>` e alinhar os nomes aos que as skills do
CTO esperam.**

### Princípios (da call + das 3 skills do CTO)
1. Separar **`Sistema`** (máquina do vault) do **conteúdo**. "Conhecimento" é um conceito, **não uma pasta-balde**.
2. **`_raw_files`** = camada bronze do conhecimento: todo input cru (reuniões, documentos, notas) guardado e **reprocessável**.
3. **"Casa = dono":** a nota mora na **entidade que a possui** (pessoa, parceiro, projeto, banco, domínio) — **não** num balde por tipo. Não existe pasta global de "Reuniões" nem balde "Conhecimento" (regra explícita da skill `transcript-extractor`).
4. **Não ter duas pastas-raiz de mesma natureza** — unificar os bancos; mesma estrutura por banco.
5. **Pessoas** no lugar de "Entrevistas" (time + negócio + recrutamento).
6. Agrupar por competência; **pasta só existe quando há conteúdo** (árvore equilibrada).
7. Vault de **um departamento só (Dados)** → o que no CTO fica sob `<área>/` sobe para a raiz (sem `Dados/` redundante).
8. Teste-guia: "navegando pelas pastas, acho a informação fácil?"

### Árvore proposta
```
DataTeamDocs/
├── CLAUDE.md · log.md                          (raiz)
├── Sistema/                                   (máquina; "_" ordena no topo; nomes batem com as skills)
│   ├── _raw_files/                             (camada BRONZE do conhecimento — cru, reprocessável)
│   │   ├── reuniões/ (pendente · processado)
│   │   ├── documentos/ (pendente · processado)
│   │   └── notas/ (pendente · processado)
│   ├── Capturas (log de populate)/             (âncoras da skill populate)
│   ├── Base de Conhecimento (Claude)/          (espelho da memória do Claude — skill sincronizar)
│   ├── _Templates/                             (← /Templates)
│   └── Skills/_catalogo.md                     (✅ já criado)
├── Arquitetura/
│   ├── Visão Geral · Stack & Medalhão
│   ├── Migração data_team/                     (← DB_instituto_experience/Limpeza e Migração)
│   └── Data Lake/                              (← /Data Lake — Jobs/Orquestração/Crawlers/Tabelas)
├── Banco de Dados/
│   └── MySQL/  ├── instituto_experience/ (Tabelas, Views, Rotinas, Eventos, Dicionário)
│               └── data_team/                  (destino da migração)
├── Fontes de Dados/                            (← "Documentações Fontes de Dados": Buygoods/Clickbank/Cartpanda)
├── Dashboards/                                 (mantém)
├── Pessoas/                                    (← Entrevistas — "casa = dono")
│   ├── <Nome>/ (1on1/ · perfil: papel, o que faz, o que melhorar)
│   └── Recrutamento/ (Triagem · Teste Técnico · Aprovados)   ← Kleriston, Júlio
├── Parceiros/<empresa>/Reuniões/               (consultorias/fornecedores) ← call Teddy
├── Reuniões/                                   (reuniões INTERNAS do time — FCA, brainstorm, planejamento)
├── Decisões/                                   (ADRs do time) ← afiliados-nutra, esta ADR-001
├── Projetos/                                   (← "Epicos")
├── Incidentes/                                 (mantém)
└── Operação/                                   (regras de negócio · indicadores · dicionário · Validações · Fluxos-N8N · Planilhas)

  ✗ "Conhecimento/" DISSOLVIDA — conteúdo vai para o dono (ver De → Para).
```

### De → Para
| Hoje | Vai para |
|---|---|
| `DB_instituto_experience` + `DB_data_team` | `Banco de Dados/MySQL/<db>` (unificados) |
| `DB_instituto_experience/Limpeza e Migração` | `Arquitetura/Migração data_team/` |
| `Data Lake` | `Arquitetura/Data Lake/` |
| `Documentações Fontes de Dados` | `Fontes de Dados/` |
| `Entrevistas` | `Pessoas/Recrutamento/` |
| `Templates` | `Sistema/_Templates/` |
| `Epicos` | `Projetos/` |
| `Validações` + `Fluxos-N8N` + `Planilhas Manuais` | `Operação/` |
| `Conhecimento/Calls` (parceiro, ex.: Teddy) | `Parceiros/<nome>/Reuniões/` |
| `Conhecimento/Calls` (interna do time) | `Reuniões/` |
| `Conhecimento/Calls` (1:1) | `Pessoas/<nome>/1on1/` |
| `Conhecimento/Decisões` (ADRs) | `Decisões/` |
| `Conhecimento/Dossiês` | distribuído na entidade dona (tabela→`Banco de Dados`; pessoa→`Pessoas`) |
| `Dashboards`, `Incidentes` | mantêm |

> **"Conhecimento/" é dissolvida** — não vira nova pasta; vira destino-por-dono acima.

## Por que dissolver "Conhecimento" (modelo do CTO)
"Conhecimento" agrupa **por tipo** (Calls/Decisões/Dossiês), desligado do dono. O CTO usa
**"casa = dono"**: a nota mora na entidade que a possui. A skill `transcript-extractor` é
explícita: *"a nota mora na entidade dona… não existe mais pasta global de Reuniões."* No vault
dele **não existe** "Conhecimento" — o único "de conhecimento" é o `Sistema/Base de Conhecimento
(Claude)/`, que é o **espelho da memória do Claude** (coisa específica, não balde). Logo, dissolver.

## Alinhar nomes às skills do CTO (reduz adaptação)
Adotar os nomes exatos que as skills esperam (`Sistema/_raw_files/{reuniões,documentos,notas}/`,
`Capturas (log de populate)/`, `Base de Conhecimento (Claude)/`, `_Templates/`, `Parceiros/<nome>/Reuniões/`,
`Pessoas/<Nome>/1on1/`, `Decisões/`) faz `populate`/`transcript-extractor`/`sincronizar-conhecimento`
rodarem quase sem alteração — sobra adaptar **dono** (Tadeu, não Gabriel) e a skip-list, e adicionar a
**regra de espelhamento no `CLAUDE.md`**.

## Consequências
### Positivas
- Navegação por domínio; fim das duas raízes de banco; base para Postgres/futuros bancos com a mesma estrutura.
- Inputs crus preservados e reprocessáveis (Raw Files) → reorganizações futuras sem perda.
- Onboarding de fontes mais previsível (Fontes de Dados + futura skill `onboard-gateway`).
### Negativas
- Migração mexe em centenas de arquivos versionados; exige `git mv` + reapontar alguns índices/wikilinks.
- Curva de ajuste até o time se acostumar com os novos caminhos.
### Neutras / observações
- Wikilinks do Obsidian são por nome de arquivo (independem de pasta) — quebram só onde houver caminho explícito.

## Ponto em aberto resolvido: "Athena entra em Banco de Dados?"
**Recomendação: não.** Athena é **engine de query sobre o Data Lake (S3)**, não banco relacional
como o MySQL (onde vivem tabelas/views/procedures/eventos). Logo, catálogo Athena/Glue fica em
`Arquitetura/Data Lake/`; `Banco de Dados/` é só para bancos relacionais.

## Alternativas consideradas
### A — Copiar a árvore do CTO (BUs/departamentos, estratégico×operacional) (rejeitada)
**Por que não**: o vault do CTO é company-wide (várias BUs); o nosso é o vault técnico do time de dados. Importamos os **princípios**, não a topologia dele.
### B — Só renomear/unir os bancos e parar por aí (parcial)
**Por que não (sozinha)**: resolve o pior sintoma, mas deixa as outras pastas soltas na raiz. Pode ser o **lote 1** se a migração total for arriscada.

## Critérios de revisão
Revisar se: a árvore criar atrito de navegação; entrar um novo banco (Postgres) ou nova classe de fonte; o time crescer e precisar de pastas por pessoa/squad.

## Próximos passos
- [ ] Tadeu revisa/ajusta esta proposta (nomes, agrupamentos).
- [ ] Ao aprovar: executar com `git mv` (preserva histórico) + corrigir índices; opção de fazer por lotes.
- [ ] (Separado) Instalar skills de ingestão quando o CTO enviar os scripts; plugins `superpowers`/`obsidian-cli` com o Davi.

## Referências
- Origem: [[2026-06-04 Sessão de trabalho — Estrutura e governança do vault (Gabriel)]] (ata) · [[2026-06-04 Sessão — Estrutura do Vault (Gabriel)]] (transcript cru)
- Relacionada: [[2026-06-03 - Alinhamento Teddy (consultoria de dados)]]
- [[Sistema/Skills/_catalogo]] · [[migracao-data_team-mapa]]
