# M3-G1 — Activation Prerequisites

## Identificação

- Release: `FR-0`
- Marco: `M3`
- Gate: `M3-G1`
- Objetivo: estabelecer os pré-requisitos verificáveis para uma futura decisão de ativação
- Estado: `IN_PROGRESS`

## Fontes normativas

Este documento não redefine ownership nem política de ativação.

As fontes canônicas são:

- política e autoridade: `governance/adr/ADR-FR0-001-ACTIVATION-POLICY.md`;
- ownership normativo: `registries/ownership-registry.v1.json`;
- plano do marco: `governance/M3-EXECUTION-PLAN.md`;
- baseline: `baseline/AB-FR0-001.json`.

A decisão normativa aplicável é:

- decision: `DEC-RELEASE-ACTIVATION`;
- decision owner: `CTX-CHANGE`;
- input: `FACT-RELEASE-LIFECYCLE`.

## Responsabilidades

| Responsabilidade | Autoridade canônica |
|---|---|
| Decisão da transição de release | `CTX-CHANGE` |
| Verificação de políticas, gates e exceções | `CTX-GOV` |
| Custódia das evidências | `CTX-EVIDENCE` |
| Evidência de prontidão operacional | `CTX-OPS` |
| Evidência de admissão de capacidade | `CTX-CAPACITY` |
| Accountable da baseline | `Rafael` |
| Revisão independente | identidade diferente do accountable |

Nenhuma responsabilidade auxiliar transfere a autoridade decisória de
`CTX-CHANGE`.

## Pré-requisitos do M3-G1

O M3-G1 somente poderá ser encerrado como `SATISFIED` quando houver evidência
verificável de todos os itens abaixo.

### G1.1 — Política rastreável

- ADR de ativação existente;
- ADR revisado;
- status do ADR formalmente resolvido;
- publicação do ADR sem alteração do estado operacional da release.

### G1.2 — Ownership inequívoco

- `DEC-RELEASE-ACTIVATION` existente uma única vez;
- `decision_owner` igual a `CTX-CHANGE`;
- input igual a `FACT-RELEASE-LIFECYCLE`;
- referências válidas nos registries canônicos;
- testes de ownership aprovados.

### G1.3 — Autoridade humana

- accountable identificado;
- revisor independente identificado;
- autoridade de operação identificada;
- autoridade de rollback identificada;
- nenhuma identidade acumulando accountability e revisão independente.

### G1.4 — Protocolo de decisão

O protocolo deverá aceitar exclusivamente:

- `ACTIVATE`;
- `DO_NOT_ACTIVATE`;
- `DEFER`.

O resultado deverá conter:

- identidade da autoridade;
- data e hora;
- release e baseline;
- evidências consideradas;
- bloqueadores;
- decisão;
- justificativa;
- referência ao rollback;
- referência à revisão independente.

### G1.5 — Protocolo de V11

Antes de qualquer execução de V11 deverão existir:

- definição formal do objetivo;
- entradas necessárias;
- ambiente de execução;
- critérios objetivos de aprovação e reprovação;
- evidências produzidas;
- responsável pela execução;
- responsável pela revisão;
- regra explícita de que ausência de execução impede qualquer alegação de aprovação.

### G1.6 — Dependências para o M3-G2

O M3-G2 não poderá iniciar enquanto:

- este gate permanecer `IN_PROGRESS`;
- o ADR permanecer sem resolução formal;
- ownership ou autoridades estiverem ambíguos;
- o protocolo de decisão estiver incompleto;
- o protocolo de V11 estiver indefinido.

## Evidências mínimas para fechamento

O pacote de fechamento do M3-G1 deverá conter:

1. ADR canônico;
2. ownership registry atualizado;
3. testes de ownership aprovados;
4. definição das autoridades humanas;
5. protocolo de decisão;
6. protocolo de V11;
7. Architecture Gate aprovado;
8. revisão independente registrada;
9. working tree limpa;
10. referência ao commit e ao pull request de fechamento.

## Critério de bloqueio

A ausência ou ambiguidade de qualquer evidência obrigatória bloqueia o gate.

Documentação isolada não autoriza ativação.

## Estado atual

`M3-G1: IN_PROGRESS`

`M3-G2: NOT_STARTED`

`FR-0 activation: NOT_AUTHORIZED`
