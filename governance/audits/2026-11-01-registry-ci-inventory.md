# Inventário verificável — registries FR-0 e CI do PR #30
**Data:** 2026-11-01  
**Estado:** EVIDENCE_COLLECTED / REVIEW_PENDING  
**Fonte:** GitHub conectado, branch principal para registries e commit `10a3da658d378124c12150402bb4c90caf34d3f1` para CI.

## 12 registries normativos recuperados
| Registry | Arquivo | Status observado |
|---|---|---|
| Context | `registries/context-registry.v1.json` | DRAFT |
| Ownership | `registries/ownership-registry.v1.json` | DRAFT |
| Invariant | `registries/invariant-registry.v1.json` | DRAFT |
| Enforcement | `registries/enforcement-registry.v1.json` | DRAFT |
| Contract | `registries/contract-registry.v1.json` | DRAFT |
| Capability | `registries/capability-registry.v1.json` | DRAFT |
| Test catalog | `registries/test-catalog.v1.json` | DRAFT |
| Traceability | `registries/traceability-registry.v1.json` | DRAFT |
| Exception | `registries/exception-registry.v1.json` | DRAFT |
| Risk | `registries/risk-registry.v1.json` | DRAFT |
| Validation graph | `registries/validation-graph.v1.json` | DRAFT |
| Work package catalog | `registries/work-package-catalog.v1.json` | DRAFT |

Todos os caminhos acima foram confirmados por leitura de arquivo no GitHub. Os arquivos mantêm `architecture_baseline_id: AB-FR0-001`; **nenhum status foi alterado**.

## Artefatos adicionais confirmados
- `baseline/AB-FR0-001.json`: `DRAFT`, requer revisão independente.
- `release/FR-0.manifest.json`: presente.
- `governance/M3-G1-ACTIVATION-PREREQUISITES.md`: presente, `IN_PROGRESS`.
- `governance/adr/ADR-FR0-001-ACTIVATION-POLICY.md`: presente, `PROPOSED`.
- `governance/M3-EXECUTION-PLAN.md`: M3-G1 em andamento; M3-G2 a G4 não iniciados.

## Evidência CI associada ao PR
- Commit observado: `10a3da658d378124c12150402bb4c90caf34d3f1`.
- GitHub Actions run: [41272168219](https://github.com/brunorafaeliecb-web/fr0-architecture/actions/runs/41272168219).
- Workflow: `architecture-gate`.
- Status: `completed`; conclusão: `success`.
- O workflow bem-sucedido não comprova, isoladamente, revisão humana independente, fechamento de M3, teste V11 ou ativação de produção.

## Pendências de auditoria
1. Conferir o conteúdo e as relações entre os 12 registries, inclusive owner único e referências cruzadas.
2. Comparar provas históricas com execuções atuais; validar SHA-256/lock e reprodutibilidade quando houver runtime apropriado.
3. Reconciliar variantes PDF protegidas do WallFrankin e duplicatas do Drive.
4. Atualizar **o BG-REG-001 existente** somente após rastreabilidade de origem e decisão apropriada.
5. Verificar política, rollback, observabilidade e revisor independente; não promover gates artificialmente.

## Integridade e limites
A evidência apresentada é uma inspeção remota do GitHub e da execução reportada pelo GitHub Actions; nenhuma alteração foi feita em código, registries, baseline, manifest ou arquivos de controle. Esta auditoria não executa `ACTIVATE`.
