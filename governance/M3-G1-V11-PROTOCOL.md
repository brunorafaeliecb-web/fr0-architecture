# M3-G1 V11 Execution Protocol

## Escopo

Este protocolo define as condições mínimas para qualquer execução de V11 relacionada à release FR-0.

## Objetivo

V11 deverá verificar, de forma reproduzível e auditável, se a release atende aos critérios definidos para a etapa correspondente do M3.

## Pré-condições

Antes da execução deverão estar definidos:

- release e baseline avaliadas;
- commit exato;
- objetivo formal da verificação;
- entradas necessárias;
- ambiente de execução;
- executor identificado;
- revisor identificado;
- critérios objetivos de aprovação;
- critérios objetivos de reprovação;
- local de custódia das evidências.

## Evidências obrigatórias

A execução deverá produzir:

- data e hora em formato ISO 8601;
- identidade do executor;
- ambiente utilizado;
- comandos ou procedimento executado;
- entradas utilizadas;
- saída completa;
- resultado;
- evidências anexadas ou referenciadas;
- identidade do revisor;
- conclusão da revisão.

## Resultados permitidos

Somente os seguintes resultados são válidos:

- `PASS`
- `FAIL`
- `NOT_EXECUTED`

## Regras de controle

- `PASS` somente poderá ser declarado após execução verificável.
- Ausência de execução implica `NOT_EXECUTED`.
- Evidência incompleta impede `PASS`.
- Falha em qualquer critério obrigatório implica `FAIL`.
- O executor não poderá aprovar a própria revisão independente.
- A execução de V11, isoladamente, não autoriza a ativação da release.

## Estado atual

- M3-G1: `IN_PROGRESS`
- FR-0 activation: `NOT_AUTHORIZED`
- V11: `NOT_EXECUTED`
