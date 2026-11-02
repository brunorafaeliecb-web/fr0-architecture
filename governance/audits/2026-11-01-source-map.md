# Mapa de fontes normativas e técnicas — BGD / WallFrankin
**Status:** PROPOSED. Caminhos externos indicam fontes identificadas, não importações aprovadas.

| Domínio | Fonte | Autoridade / estado |
|---|---|---|
| Constituição | [Volume I](https://drive.google.com/file/d/1aCID7Bc8rEVEP_yIJg2dCX5qFmFnCwcH/view) | APPROVED BASELINE v1.0.0 no documento |
| Nomenclatura | [BGD 00006 v1.b](https://drive.google.com/file/d/1grJbxIxPpKl6efnsgUdPEMMShmLArFu_/view) | CANÔNICO |
| Catálogo de decisões | [BGD 00031](https://drive.google.com/file/d/19Xwuc3Nn9vxfs5h3-pFWAst8d4TEq_mq/view) | CANÔNICO |
| Padrão documental | [BGD 00033](https://drive.google.com/file/d/1DHLZTv4X8KtawUc0iVHhRUaB0JhLSKzu/view) | CANÔNICO |
| Registro mestre | [BG-REG-001](https://docs.google.com/document/d/1XcyrYAeN9q4SJdXyp_YHTpmlo3Qfu1FgyB3NFDxwo3s/edit) | IN_PROGRESS; não duplicar |
| WallFrankin | WF-CONSOLIDATED-01..10, documentos nos Drives | DRAFT_CONSOLIDATED / NOT_AUTHORIZED |
| Registry técnico | [Ownership](../../registries/ownership-registry.v1.json) | DRAFT |
| Contextos | [Context Registry](../../registries/context-registry.v1.json) | DRAFT |
| Baseline | [AB-FR0-001](../../baseline/AB-FR0-001.json) | DRAFT |
| Decisão de ativação | [ADR-FR0-001](../adr/ADR-FR0-001-ACTIVATION-POLICY.md) | PROPOSED |
| Planejamento de ativação | [M3](../M3-EXECUTION-PLAN.md) | IN_PROGRESS |

## Nomenclatura BGD
Para documentos sujeitos ao padrão, utilizar `NNNNN.vX.r.DD.MM.AA-NOME-ABREV.ext`. O número lógico deve vir de registro competente; nunca inferir sequência livre por busca parcial. Estes dois arquivos são **registros operacionais de auditoria em branch de revisão** e não recebem identificação canônica nova até reconciliação com o Registro Mestre.

## Regras de integração
1. GitHub é fonte do código versionado, registries e evidências de CI.
2. Drive conserva originais documentais e suas decisões.
3. Dropbox pode armazenar cópias de segurança verificadas, sem substituir os originais.
4. Divergências exigem decisão registrada; arquivos com nomes semelhantes não são automaticamente equivalentes.
5. Sem execução, revisão independente e aprovação humana, permanece `NOT_AUTHORIZED`.
