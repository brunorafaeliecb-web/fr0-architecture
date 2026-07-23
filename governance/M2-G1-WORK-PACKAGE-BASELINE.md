# M2-G1 Work Package Baseline

## Identificação

- Release: `FR-0`
- Marco: `M2`
- Gate: `M2-G1`
- Status: `SATISFIED`
- Modelo: `INDIVIDUAL_BOOTSTRAP`

## Objetivo

Confirmar o escopo, a sequência, as dependências e os critérios mínimos
de aceite dos work packages que compõem a implementação controlada do FR-0.

## Work packages

| Ordem | Work package | Nome | Dependências |
|---:|---|---|---|
| 1 | FR0-WP-001 | Normative Registry Schemas | Nenhuma |
| 2 | FR0-WP-002 | Context and Ownership Baseline | FR0-WP-001 |
| 3 | FR0-WP-003 | Foundation Type Library | FR0-WP-001, FR0-WP-002 |
| 4 | FR0-WP-004 | Canonical Contract Envelope | FR0-WP-001, FR0-WP-003 |
| 5 | FR0-WP-005 | Architecture Test Engine | FR0-WP-001 a FR0-WP-004 |
| 6 | FR0-WP-006 | CI Architecture Gate | FR0-WP-005 |
| 7 | FR0-WP-007 | Architecture Baseline Workflow | FR0-WP-001 a FR0-WP-006 |
| 8 | FR0-WP-008 | Release Manifest Generator | FR0-WP-001 a FR0-WP-007 |

## Regras de execução

Cada work package deverá:

- possuir issue própria;
- declarar dependências;
- possuir critérios de aceite verificáveis;
- produzir artefatos versionados;
- incluir testes adequados ao escopo;
- manter rastreabilidade com `AB-FR0-001`;
- passar pelo workflow `architecture-gate`;
- registrar evidência de conclusão;
- não ser encerrado com critérios pendentes.

## Estratégia de entrega

1. Implementar um work package por vez.
2. Utilizar branch específica para cada work package.
3. Abrir pull request contra `main`.
4. Exigir o architecture gate verde.
5. Fazer merge somente após verificação dos critérios de aceite.
6. Atualizar o work package catalog e as evidências quando necessário.

## Decisão do gate

O escopo e as dependências dos oito work packages estão confirmados.

`M2-G1: SATISFIED`

A implementação controlada está autorizada a avançar para `M2-G2`.
