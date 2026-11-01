# Evidências recuperadas de conversas e Biblioteca ChatGPT
**Data:** 2026-11-01  
**Estado:** AUDIT_FINDING / REVIEW_PENDING  
**Origem:** busca sobre anexos históricos e arquivos da Biblioteca do usuário, além do Drive e GitHub já examinados.

## Achado prioritário — versões constitucionais distintas
1. `BrasilGuard_Volume_I_Fundacao_Estrategia_Visao_v1.0.0_APPROVED.md`: `BGP-VOL1-FSV-001`, `APPROVED BASELINE`, v1.0.0, 13/07/2026.
2. `BGP-VOL1-FSV-001-v1.1.0-rc2.pdf` e correspondente `.docx`: v1.1.0-rc2, 14/07/2026, **CANDIDATE BASELINE**, não aprovado.
3. `BGP-VOL1-FSV-001-GAP-REPORT-v1.1.0-rc2.docx`: relatório de lacunas encontrado; declara explicitamente que a rc2 **não pode ser promovida a APPROVED BASELINE** enquanto não houver rastreabilidade, evidências técnicas, revisão formal e gates.

**Conclusão:** não há contradição em manter v1.0.0 como baseline aprovada e v1.1.0-rc2 como revisão candidata posterior. Versão numericamente mais recente **não** equivale a versão vigente. Nunca substituir v1.0.0 pela rc2 sem decisão formal e evidências de fechamento.

## Achado — manual de identidade visual
Arquivo histórico encontrado na Biblioteca: `Manual de Identidade Visual Brasilguard.png`. É uma imagem/prancha de manual de marca com versões do logotipo, paleta, tipografia, usos e espaçamento. **Não comprova** a existência de um manual integral editável ou a versão normativa final. Guardar a origem e submeter à verificação visual e de integridade.

## Achado — fontes adicionais do corpus
- `00006.v1.b.04.09.26-PADRAO-NOMES-BGD-CANON.md`.
- `00031.v1.a.04.09.26-CATALOGO-DECISOES-BGD.md`.
- `WallFrankin_Consolidado_Parte_04_Governanca_ADRs_Registries_Baselines_Gates.md`.
- Relatório de auditoria `RELATORIO-AUDITORIA-BGD-WALLFRANKIN.md` também existente na Biblioteca; não confundir com evidência operacional.
- Anexo histórico `Texto colado(19).txt` contendo comandos do repositório local `D:\\GitHub\\fr0-architecture`; requer inspeção de conteúdo pertinente antes de qualquer afirmação de estado do ambiente local.

## Lacunas específicas documentadas na rc2
O GAP-REPORT identifica 10 achados GAP-001..010, inclusive bloqueadores:
- Perfis/princípios incompletos.
- Ausência de matriz princípio → requisito → risco → ADR → teste → evidência.
- Métricas sem protocolos/baseline.
- Evidências técnicas e aprovações formais ausentes.
- Testes, threat models, retenção, risco residual e prontidão dependentes de artefatos verificáveis.

O checklist CHK-001..CHK-013 do relatório deixa a rc2 em CANDIDATE até fechamento auditado.

## Próxima decisão governada
1. Registrar v1.0.0 e v1.1.0-rc2 como **dois estados da mesma linha documental**, sem substituição.
2. Confrontar o registro mestre `BG-REG-001` com estes artefatos e os anexos preservados.
3. Preservar a imagem do manual de marca como referência preliminar, sem atribuir aprovação.
4. Preservar `FR-0 activation: NOT_AUTHORIZED`.
5. Não copiar anexos de classificação L3 para repositório sem revisão de classificação e autorização de exposição. Este arquivo contém somente metadados e síntese.

## Limitações
A busca na Biblioteca retornou correspondências relevantes, não uma enumeração exaustiva de todas as conversas e todos os anexos. Falta inspeção completa das variantes e um manifesto de hashes dos binários recuperados. Nenhuma aprovação ou ativação foi realizada.
