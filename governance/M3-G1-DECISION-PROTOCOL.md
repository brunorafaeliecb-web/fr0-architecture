# M3-G1 Release Activation Decision Protocol

## Escopo

Este protocolo define o formato obrigatório para qualquer decisão sobre a ativação da release FR-0.

## Decisões permitidas

Somente os seguintes resultados são válidos:

- `ACTIVATE`
- `DO_NOT_ACTIVATE`
- `DEFER`

Qualquer outro valor torna a decisão inválida.

## Autoridade decisória

- Decision: `DEC-RELEASE-ACTIVATION`
- Decision owner: `CTX-CHANGE`
- Accountable da baseline: Rafael

A autoridade decisória deverá ser identificada nominalmente no registro final.

## Conteúdo obrigatório

Toda decisão deverá registrar:

- identidade da autoridade;
- data e hora em formato ISO 8601;
- release;
- baseline;
- commit avaliado;
- evidências consideradas;
- bloqueadores identificados;
- decisão;
- justificativa;
- referência ao plano de rollback;
- referência à revisão independente.

## Regras de bloqueio

`ACTIVATE` não poderá ser emitido quando:

- houver evidência obrigatória ausente;
- existir bloqueador aberto;
- o rollback não estiver definido e validado;
- a revisão independente não estiver registrada;
- V11 não tiver sido executado de forma verificável;
- o Architecture Gate não estiver aprovado.

Nessas condições, o resultado deverá ser `DO_NOT_ACTIVATE` ou `DEFER`.

## Estado atual

- M3-G1: `IN_PROGRESS`
- FR-0 activation: `NOT_AUTHORIZED`
- V11: `NOT_EXECUTED`
