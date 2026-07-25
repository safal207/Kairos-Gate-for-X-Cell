# BioEvidence OS — Prioritized Backlog

Roadmap epic: #24

This backlog is ordered by dependency. Do not start a lower item when it would expand or destabilize unfinished higher-priority work.

## COMPLETED — v0.1 core

### P0.1 Partner-laboratory evidence handoff — #25

- [x] Skill contract
- [x] Schema
- [x] Nfkbia handoff record
- [x] Validator
- [x] Fail-closed false-authorization fixture
- [x] Release gate
- [x] Human-readable report
- [x] CI integration
- [x] README and PR synchronization
- [x] Positive handoff accepted on exact-head CI
- [x] Scientific-review-to-execution leakage blocked

Verdict:

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```

## NOW — freeze v0.1

### P0.2 Freeze and review PR #23 — #26

- [x] Finish #25
- [ ] Stop adding major modules
- [ ] Inspect review threads and reviews
- [ ] Run final exact-head CI after freeze changes
- [ ] Verify schemas, examples, validators, reports, README, roadmap, backlog, and workflow agree
- [ ] Safety and overclaim scan
- [ ] Architecture diagram
- [ ] Release notes
- [ ] Request biology review
- [ ] Request statistics review

Definition of done:

- bounded v0.1 release candidate;
- no unresolved P0/P1 findings;
- explicit deferred v0.2 scope;
- exact-head evidence recorded after the freeze.

## NEXT — model and data layer

### P1.1 NVIDIA BioNeMo compatibility gate — #27

- [ ] Open separate v0.2 branch and PR
- [ ] Build model registry
- [ ] Add modality and species checks
- [ ] Add context and temporal checks
- [ ] Add training-overlap and domain-shift checks
- [ ] Add license and compute fields
- [ ] Build Model Evidence Passport
- [ ] Add positive and negative fixtures
- [ ] Produce current mouse-case compatibility report
- [ ] Produce accepted-with-limits human example

Definition of done:

- every scientific model run has a compatibility verdict and reproducibility passport;
- model output cannot silently exceed its evidence boundary.

### P1.2 Find temporally compatible human macrophage evidence — #28

- [ ] Search human macrophages
- [ ] Search monocytes and related immune activation systems
- [ ] Require pre-state to later-response linkage
- [ ] Require independent biological units
- [ ] Require technical lineage
- [ ] Resolve GSE94383 ID prefixes
- [ ] Preserve rejected candidates and reasons
- [ ] Refresh direct-replication gap

Definition of done:

Either an eligible independent dataset with a frozen analysis plan, or a complete documented gap and partner-laboratory requirement.

## THEN — product

### P1.3 Accession-to-evidence MVP — #29

- [ ] Study-intake screen
- [ ] Accession and DOI resolution
- [ ] Experimental-unit view
- [ ] Provenance/confounder graph
- [ ] Temporal and identity view
- [ ] Replication candidates
- [ ] Causal-hypothesis view
- [ ] Claim firewall
- [ ] Model compatibility view
- [ ] Partner-handoff export
- [ ] JSON evidence export
- [ ] GSE141064 reference demo
- [ ] Demo video

Definition of done:

A user enters `GSE141064` and receives the current evidence verdicts without manual report editing.

## PUBLICATION AND OUTREACH

### P1.4 Technical report and scientific outreach — #30

- [ ] Draft manuscript
- [ ] Document methods and limitations
- [ ] Link exact code, schemas, hashes, and artifacts
- [ ] Include negative and inconclusive findings
- [ ] Request biology review
- [ ] Request statistics review
- [ ] Prepare ten focused contacts
- [ ] Contact study authors
- [ ] Prepare partner-laboratory discussion package
- [ ] Prepare NVIDIA/BioNeMo one-pager
- [ ] Prepare NVIDIA Inception inputs

Definition of done:

A public reproducible draft exists and external review has begun.

### P1.5 Real biology partner pilot and agentic-biopharma positioning

Dependency: begin only after the v0.1 freeze and use the stable evidence contracts without adding major modules to PR #23.

- [ ] Obtain informed agreement from one molecular-biology partner through a trusted introduction
- [ ] Run a 30-minute discovery interview about evidence bottlenecks, repeated work, unreliable AI outputs, and expensive validation decisions
- [ ] Select one bounded cancer-biology hypothesis, DOI, accession, or evidence package
- [ ] Freeze the scientific question, competing hypotheses, allowed claims, prohibited claims, and confidentiality boundary
- [ ] Run the experimental-unit audit
- [ ] Build the provenance and confounder graph
- [ ] Search for genuinely independent replication
- [ ] Rank causal explanations without declaring a causal winner
- [ ] Apply temporal and identity-linkage gates where relevant
- [ ] Generate a machine-readable and human-readable Next Evidence Plan
- [ ] Produce a partner-laboratory evidence handoff that does not include operational wet-lab instructions
- [ ] Request independent biology and statistics review
- [ ] Agree whether the result may be public, anonymized, or private
- [ ] Turn the reviewed pilot into a reproducible case study or documented negative result
- [ ] Prepare a one-page integration brief for BIOPTIC and other AI-for-science teams
- [ ] Position Kairos as an evidence and governance layer: claim-level QA, evidence passports, multi-agent traceability, contradiction detection, and scientific red-flag gates
- [ ] Separate asset-discovery recall from scientific support for each generated claim
- [ ] Define a small non-clinical integration pilot using public or partner-approved evidence only

Definition of done:

- one real partner question audited end to end;
- one exact-version evidence package produced;
- biology and statistics review requested and dispositions recorded;
- confidential material remains protected;
- one reviewed case study or documented gap exists;
- one focused AI-for-science integration brief exists;
- no therapeutic, clinical, execution, or “cure cancer” claim is made.

## LATER

### P2 Research operations

- [ ] Automated repository surveillance
- [ ] Negative-result memory ledger
- [ ] Dataset registry
- [ ] Model registry refresh automation
- [ ] Scientific risk register
- [ ] Decision supersession ledger

### P2 Business modes

- [ ] Biotech evidence-audit report
- [ ] Academic laboratory review package
- [ ] Journal reviewer mode
- [ ] Investor/funder due-diligence mode

### P3 Expansion gates

Do not begin until v0.1 is reviewed and at least one independent or partner-generated evidence path exists.

- [ ] Additional inflammatory pathways
- [ ] Additional cell systems
- [ ] Tissue or organoid evidence layer
- [ ] Translational evidence layer

## Stop list

Do not:

- add more major modules to PR #23;
- treat cells or technical containers as biological replication;
- lower temporal or identity standards to accept a dataset;
- claim direct causality from a ranked hypothesis;
- treat a model embedding as biological validation;
- interpret scientific-review readiness as authorization to execute;
- hide null or negative evidence;
- start the MVP before the core contracts are stable.

## Weekly review template

```text
Supported this week:
Weakened or blocked:
Still unknown:
Highest-information next action:
Issue to close before new scope:
Evidence artifact produced:
External review requested:
```
