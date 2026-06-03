---
tipo: dossie
tags: [dossie, conhecimento, tabela]
objeto: <nome_real_da_tabela>
schema: instituto_experience
criticidade: <core | secundaria | arquivo | backup | controle>
status: <ativa | em-revisao | deprecated | arquivada>
ultima_revisao: {{date:YYYY-MM-DD}}
---
# 🗃️ Dossiê — {{title}}

> [!info] Resumo em 1 linha
> <Uma frase: o que essa tabela representa e qual é o ciclo de vida da linha.>

> Nota técnica gerada: [[{{title}}]] (pasta `Tabelas/`). Este dossiê é a camada **curada** — não é sobrescrito pelos scripts.

## Identificação

| Campo | Valor |
|---|---|
| **Schema** | `instituto_experience` |
| **Tabela** | `<nome>` |
| **Engine** | `InnoDB` |
| **Charset** | `utf8mb4` |
| **Volume aproximado** | `<linhas — ver nota gerada [[{{title}}]]>` |
| **Crescimento** | `<append-only | mutável | mista>` |

## Propósito

<2–4 parágrafos. Por que essa tabela existe? Qual papel ela desempenha no
pipeline? O que **não** mora aqui (escopo)? Decisões de design relevantes.>

## Estrutura

### Colunas-chave

| Coluna | Tipo | Nulo? | Descrição / uso |
|---|---|---|---|
| `id` | `bigint unsigned AI` | NO | PK |
| `<col>` | `<tipo>` | <YES/NO> | <descrição> |

### Indexes / chaves

| Nome | Colunas | Tipo | Quem usa |
|---|---|---|---|
| `PRIMARY` | `(id)` | PK | — |
| `<idx_nome>` | `(col1, col2)` | <UNIQUE/KEY> | <procedure/query> |

## Quem escreve / Quem lê

> Confira a nota gerada [[{{title}}]] (seções *Quem escreve aqui* / *Quem lê daqui*)
> e o painel **Backlinks** para a lista automática.

### Escreve
- `[[<rotina>]]` — `<INSERT/UPDATE/DELETE>` em `<contexto>`

### Lê
- `[[<rotina/view/dashboard>]]` — `<contexto da leitura>`

## Ciclo de vida da linha

1. **Nascimento**: `<onde nasce, com qual status inicial>`
2. **Transições**: `<quem promove o estado e em que condições>`
3. **Fim**: `<quando é arquivada / deletada / nunca>`

## Retenção / particionamento

<Política de purga, arquivamento ou particionamento. Se não há, registrar isso.>

## Pegadinhas e notas operacionais

> [!warning] <título da pegadinha>
> <descrição. Ex: AUTO_INCREMENT muito acima do nº de linhas — gap histórico,
> não usar pra contar volume.>

- `<pegadinha 1>`

## Queries úteis

```sql
-- <descrição>
<query>
```

## Histórico de mudanças relevantes

| Data | Mudança | Link |
|---|---|---|
| {{date:YYYY-MM-DD}} | Dossiê criado | — |

## Referências

- Nota técnica gerada: [[{{title}}]]
- MOC relacionado: [[<MOC>]]
- Decisões relacionadas: [[<Decisao>]]
