# BrasilGuard / WallFrankin — estado consolidado de recuperação
Data: 2026-11-01
Estado: RECOVERY_EVIDENCE_RECORDED / RECONCILIATION_PENDING

## Âmbito e fontes
- Drive NOCODE: corpus organizado, handoff IA, inventários históricos, 10 partes WallFrankin, documentação BrasilGuard e complementos.
- Biblioteca de conversas: versões constitucionais v1.0.0 e v1.1.0-rc2, relatório de lacunas rc2 e prancha do Manual de Identidade Visual.
- GitHub: repositório fr0-architecture, 12 registries, AB-FR0-001, release manifest, testes e gates.
- Drive IECB: registro mestre BG-REG-001 ainda em andamento.

## Integridade histórica
O inventário do handoff registra 152 caminhos. Evidência coletada nesta auditoria anterior: pacote-fonte de 12.849.803 bytes, SHA-256 bdd17c594b354341aa18df71b939c597369e0e3b85aa6dfec12056871721e7e9. Registros da auditoria apontam 138/138 arquivos do ZIP principal confrontados e 5 ZIPs externos conferidos, correspondendo a 144/152 entradas verificadas criptograficamente. Oito complementos restantes foram localizados, mas não tiveram hash atual recalculado. Esses números são **escopados ao corpus histórico de 12/08/2026**, não a todos os artefatos posteriores.

## Fontes navegáveis
- Corpus organizado: https://drive.google.com/drive/folders/1DJLHLIEVWPS4mV15DSK2i2eo7fPFnbj8
- Handoff IA: https://drive.google.com/drive/folders/1XSKfu9BQhb9Qs-_Zm8gptAzDOYsSeKxw
- ZIP-fonte: https://drive.google.com/file/d/1C1BZxNacmi1EtMB4BlV5CGE0HVL3tN5M/view
- Inventário de integridade: https://drive.google.com/drive/folders/1j-hGVZmEQhX36EZpii35yLZm3pevejks
- Inventário de reconciliação: https://docs.google.com/spreadsheets/d/1GkMYp4WHFTZZLVdImzfXrA07B8oum5UXGf-GA88oz3s/edit
- Registro Mestre existente: https://docs.google.com/document/d/1XcyrYAeN9q4SJdXyp_YHTpmlo3Qfu1FgyB3NFDxwo3s/edit

## Governança e precedência
1. Constituição BGP-VOL1-FSV-001 v1.0.0: APPROVED BASELINE no próprio documento.
2. Constituição BGP-VOL1-FSV-001 v1.1.0-rc2: CANDIDATE BASELINE; relatório GAP-REPORT registra bloqueadores; não substituir automaticamente v1.0.0.
3. WallFrankin consolidado partes 01–10: DRAFT_CONSOLIDATED / NOT_AUTHORIZED.
4. AB-FR0-001, registries: DRAFT; ADR-FR0-001: PROPOSED; M3-G1: IN_PROGRESS; demais gates M3 conforme plano.
5. Decisão humana independente e testes operacionais seguem exigidos antes de ativação. Deploy != ativação.

## Pendências para concluir
- Recalcular os 8 hashes externos não concluídos.
- Reconciliar variantes PDF PROTEGIDO/PROTEGIDO_MAXIMO e revisões históricas sem apagar originais.
- Conciliar fontes de setembro/outubro/novembro com corpus de agosto e BG-REG-001, sem gerar um registro concorrente.
- Verificar o manual de identidade visual integral e sua aprovação, distinguindo a prancha recuperada.
- Validar testes e CI atuais, vínculos entre registries, revisão independente, readiness V11, rollback e observabilidade.
- Criar e verificar backup separado no Dropbox quando sua estrutura de destino estiver aprovada; nenhum backup remoto deve ser declarado sem readback.

## Limites desta atualização
Esta mudança é DOCUMENTAL E ADITIVA, exclusivamente na branch do PR #30. Nenhum binário original ou documento L3 foi publicado no GitHub; foram registrados apenas caminhos, hashes e estados de governança. Não modifica main, baseline, release, registries, gates nem decisões.
