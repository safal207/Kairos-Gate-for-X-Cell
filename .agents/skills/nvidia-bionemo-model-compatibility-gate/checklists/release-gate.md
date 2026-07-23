# BioNeMo compatibility release gate

Release only when all checks pass:

- [ ] Dataset identity, organism, modality, temporal design and intended claim are frozen.
- [ ] Model family, checkpoint, version, source and runtime are exact.
- [ ] Official source documentation is recorded with retrieval date.
- [ ] Input representation and every transformation are explicit.
- [ ] Species and cell-context compatibility are evaluated.
- [ ] Training/benchmark overlap is assessed or remains a visible HOLD.
- [ ] Agent/tool orchestration is not counted as biological evidence.
- [ ] Evidence contribution and blocked claims are explicit.
- [ ] Every executed run has input/output hashes, parameters, seeds and runtime metadata.
- [ ] Mouse Geneformer cannot be accepted without transfer validation.
- [ ] DNA/protein models cannot answer unrelated cell-state questions.
- [ ] Positive and misuse fixtures pass/fail as intended.
- [ ] No physical biological execution is authorized.
