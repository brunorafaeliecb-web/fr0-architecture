# ADR-FR0-001 — Activation Policy and Authority

## Status

`PROPOSED`

## Contexto

O FR-0 possui baseline, registries, validação V0–V8, Architecture Gate,
release manifest e evidências determinísticas.

A publicação do manifesto não representa ativação. A transição da release
para um estado ativo exige autoridade inequívoca, evidências operacionais,
revisão independente e rollback validado.

A Constituição da Engenharia determina:

- arquitetura baseada em bounded contexts;
- observabilidade como requisito para produção;
- decisões estruturais formalizadas por ADR;
- evolução técnica rastreável.

## Decisão

O bounded context `CTX-CHANGE` é o único owner semântico e de transição do
ciclo de vida da release.

A decisão de ativação pertence exclusivamente a `CTX-CHANGE`, pois o fato
canônico `FACT-RELEASE-LIFECYCLE` possui:

- `semantic_owner: CTX-CHANGE`;
- `transition_owner: CTX-CHANGE`.

Os demais contextos participam sem assumir a decisão:

- `CTX-GOV` verifica políticas, gates, baseline e exceções;
- `CTX-EVIDENCE` mantém os registros de evidência;
- `CTX-OPS` fornece evidências de prontidão operacional;
- `CTX-CAPACITY` fornece evidência de admissão de capacidade.

## Autoridade humana

O accountable da baseline permanece `Rafael`.

A revisão independente é obrigatória e não pode ser executada pela mesma
identidade accountable.

A autoridade humana não substitui o owner arquitetural. Ela atua dentro do
processo governado por `CTX-CHANGE`.

## Pré-requisitos de ativação

Uma decisão `ACTIVATE` somente poderá ocorrer quando existirem evidências
verificáveis de:

1. validação arquitetural aplicável;
2. Architecture Gate aprovado;
3. observabilidade operacional;
4. capacidade e dependências elegíveis;
5. rollback definido e validado;
6. revisão independente aprovada;
7. execução controlada e verificável de V11;
8. ausência de bloqueadores abertos.

Ausência de qualquer pré-requisito resulta em `DEFER` ou
`DO_NOT_ACTIVATE`.

## Estados de decisão

Os únicos resultados permitidos são:

- `ACTIVATE`;
- `DO_NOT_ACTIVATE`;
- `DEFER`.

A criação, aprovação ou publicação deste ADR não altera o estado da release.

`FR-0 activation: NOT_AUTHORIZED`

## Consequências

### Positivas

- elimina ambiguidade de ownership;
- preserva separação entre governança e transição de release;
- mantém evidências em fonte própria;
- impede ativação documental ou implícita;
- fornece base rastreável para o M3-G1.

### Custos

- exige atualização normativa do ownership registry;
- exige evidências operacionais antes de V11;
- exige revisão independente;
- impede atalhos de ativação.

## Restrições

- `CTX-GOV` não pode assumir o ownership da release;
- `CTX-EVIDENCE` não pode decidir com base nas evidências que armazena;
- `CTX-OPS` não pode autorizar ativação isoladamente;
- aprovação documental não equivale a ativação;
- V11 não pode ser presumido ou declarado sem execução;
- rollback não pode existir apenas como intenção.

## Próximas ações

Antes de alterar o status deste ADR para `ACCEPTED`:

1. registrar a decisão de ativação no ownership registry;
2. definir os pré-requisitos verificáveis do M3-G1;
3. executar os testes e atualizar o lock determinístico;
4. passar pelo Architecture Gate;
5. registrar revisão independente.
