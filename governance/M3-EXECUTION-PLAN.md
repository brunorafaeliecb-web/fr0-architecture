# M3 Execution Plan — Activation Readiness

## Identificação

- Release: `FR-0`
- Marco: `M3`
- Issue pai: `#23`
- Objetivo: preparar uma decisão controlada de ativação
- Estado do marco: `IN_PROGRESS`

## Princípio de controle

O M3 prepara a decisão de ativação, mas não autoriza ativação
automaticamente.

A release permanece não ativa até uma decisão formal, explícita,
auditável e sustentada por evidências.

## Gates

| Gate | Objetivo | Status |
|---|---|---|
| M3-G1 | Política e pré-requisitos de ativação | IN_PROGRESS |
| M3-G2 | Evidências operacionais e rollback | NOT_STARTED |
| M3-G3 | Revisão independente e execução controlada de V11 | NOT_STARTED |
| M3-G4 | Decisão formal de ativação e encerramento | NOT_STARTED |

## Resultados possíveis

A decisão final do M3 deverá ser uma das seguintes:

- `ACTIVATE`
- `DO_NOT_ACTIVATE`
- `DEFER`

## Restrições

- Publicação não implica ativação.
- A ativação permanece falsa até decisão explícita.
- V11 somente poderá ser declarado após execução verificável.
- Revisão independente é obrigatória.
- Rollback deve estar definido e validado.
- Ausência de evidência bloqueia a ativação.
- Aprovação documental isolada não autoriza ativação operacional.

## Estado inicial

`M3-G1: IN_PROGRESS`

`FR-0 activation: NOT_AUTHORIZED`
