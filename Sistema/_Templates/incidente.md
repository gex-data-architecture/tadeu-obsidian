---
tipo: incidente
tags: [incidente, conhecimento]
data: {{date:YYYY-MM-DD}}
severidade: <SEV1 | SEV2 | SEV3>
status: <aberto | em-investigacao | resolvido>
owner: Tadeu
sistemas_afetados: [<ex: dashboard X>]
---
# 🚨 {{title}}

> [!warning] Status atual
> `<aberto | em-investigacao | resolvido>` · Sev `<SEV1|SEV2|SEV3>` · Owner `<nome>`

## Resumo (TL;DR)

<2–3 frases. O quê quebrou, quanto durou, qual impacto.>

## Severidade e impacto

| Item | Valor |
|---|---|
| **Severidade** | `<SEV1|SEV2|SEV3>` |
| **Início** | {{date:YYYY-MM-DD}} `<HH:MM>` |
| **Detecção** | {{date:YYYY-MM-DD}} `<HH:MM>` |
| **Resolução** | `<HH:MM>` |
| **Duração total** | `<X h Y min>` |
| **Sistemas afetados** | `<...>` |
| **Detecção feita por** | `<alerta | usuário | revisão | outro>` |

## Linha do tempo

| Hora | Evento |
|---|---|
| `<HH:MM>` | <evento> |

## Causa-raiz

> [!info] Investigar o SISTEMA, não a pessoa
> Se a causa parece ser "humano clicou errado", a causa real é "sistema permitiu clicar errado".

<Descrição técnica da causa-raiz. Linke o objeto culpado: [[<tabela/rotina>]].>

## Correção aplicada

<O que foi feito para resolver.>

## Lições aprendidas

### O que funcionou
- <ponto>

### O que não funcionou
- <ponto>

### Ações de follow-up

| Ação | Owner | Prazo | Status |
|---|---|---|---|
| <ação> | `<nome>` | `<AAAA-MM-DD>` | 🔴 aberto |

## Referências

- Incidentes similares: [[<...>]]
- Runbook usado: [[<...>]]
