# SynTnpB 2026 — AI-designed nuclease claim audit

## Audit identity

- **Case:** `syntnpb-science-aed6123-2026`
- **Contract:** `0.2.0-preview.4`
- **Primary publication:** *Structure and evolution-guided design of minimal RNA-guided nucleases*
- **Journal:** *Science*
- **DOI:** `10.1126/science.aed6123`
- **Publication date:** 2026-07-16
- **Primary publication page:** https://www.science.org/doi/10.1126/science.aed6123
- **Abstract record:** https://pubmed.ncbi.nlm.nih.gov/41573840/
- **Structural record:** https://www.rcsb.org/structure/9YYG
- **News claim under audit:** an iXBT report framed the work as a synthetic CRISPR that surpassed natural enzymes and opened medical and agricultural applications.

## System boundary

This is a computational and documentary evidence audit. It contains no protein or DNA sequence, physical protocol, delivery method, concentration, optimization recipe, or authorization for biological execution.

## What the study supports

The paper reports a hybrid design pipeline combining structure-guided inverse protein folding, evolution-informed residue constraints, and laboratory screening. The designed entities are proposed **protein amino-acid sequences**. Physical proteins and cellular evidence were produced by the research team, not autonomously by the model.

The bounded evidence supports the following statements:

1. The peer-reviewed publication reports divergent TnpB candidates with functional RNA-guided nuclease activity after laboratory construction and screening.
2. It reports mixed comparator results for selected SynTnpB variants in bacterial-cell test contexts, and that some selected variants retained or exceeded the activity of the study's named wild-type TnpB reference in plant-cell and human-cell test contexts.
3. The deposited RCSB structure `9YYG` supports structural characterization of a selected active divergent variant.

```text
BOUNDED_VERDICT = ACCEPT_WITH_LIMITS
```

## Comparator boundary

The load-bearing comparator is the **wild-type TnpB reference used by the study**.

Therefore:

```text
some selected SynTnpB > study wild-type TnpB
in reported assay contexts
```

is not equivalent to:

```text
SynTnpB > Cas9
SynTnpB > Cas12
SynTnpB > every natural nuclease
SynTnpB is the best editor for every target or delivery system
```

Universal cross-editor superiority is blocked unless evidence directly benchmarks representative editors across prespecified targets, systems, endpoints, and safety dimensions.

## Evidence authority — preview.4

The evidence ladder records **authority and reproducibility**, not scientific prestige. A peer-reviewed finding can be real and important while remaining F2 when this audit has not reconstructed an executable evidence artifact.

```text
F2 = peer-reviewed or repository-reported observation
F3 = digested executable analysis or reproducibility bundle
F4 = deposited repository record or explicit author/laboratory confirmation
F5 = frozen unrelated-laboratory replication or risk evidence
```

Consequences for this case:

- the functional bacterial, plant-cell, and human-cell statements currently enter the machine-readable audit as **F2 publication reporting**;
- they are not promoted to F3 merely because the paper is peer reviewed;
- F3 would require a reconstructed or computed artifact with a SHA-256 digest and executable or reproducibility semantics;
- the RCSB PDB `9YYG` deposit qualifies as F4 structural confirmation for the selected structure;
- independent replication remains unestablished because no provenance-bearing F5 unrelated-laboratory object is registered.

## Evidence ladder

| Layer | Current authority | Allowed interpretation | Prohibited escalation |
|---|---|---|---|
| AI design | Publication reports inverse-folding proposals constrained by structure and evolution | The computational strategy proposed divergent TnpB sequences | “AI autonomously created the complete validated system” |
| Functional screening | Peer-reviewed reported cellular results, F2 | Molecular activity was reported in those test contexts | Executable replication, universal platform superiority |
| Comparator performance | Peer-reviewed reported named-comparator results, F2 | Some selected variants exceeded the study wild-type TnpB reference in reported contexts | Superiority over Cas9, Cas12, or all natural editors |
| Human-cell assay | Reported editing activity in a human-cell system, F2 | Human-cell molecular activity | Clinical safety or therapeutic efficacy |
| Plant-cell assay | Reported editing activity in a plant-cell system, F2 | Plant-cell molecular activity | Field readiness, ecological safety, or agricultural deployment |
| Cryo-EM | Deposited structure `9YYG`, F4 | A selected variant has a repository-confirmed structural record | Complete causal mechanism, safety, delivery, or broad superiority |
| Publication | Peer-reviewed originating-collaboration report | The findings were published after journal review | Independent unrelated-laboratory replication |

## Candidate-denominator boundary

A complete screening denominator requires explicit reconciliation across every represented stage:

```text
generated = excluded_before_screen + screened
screened = failed_screen + selected
```

Partial reporting permits unknown stages, but it does not permit impossible known counts. Whenever the corresponding values are known:

```text
screened <= generated
selected <= screened
selected <= generated
excluded_before_screen <= generated
failed_screen <= screened
```

The public abstract and news summaries describe thousands of computational variants and high-throughput screening, but this audit cannot currently fill the complete reconciliation equations.

Unresolved fields include:

- exact generated count;
- candidates excluded before screening;
- exact screened count;
- failed-screen count;
- exact selected count;
- complete failed-candidate reporting;
- whether winner-selection rules were prespecified before observing all outcomes;
- target-by-target and system-by-system performance distributions;
- how strongly the selected cryo-EM variant represents the full designed library.

```text
DENOMINATOR_COMPLETENESS = partial
SELECTION_BIAS_STATUS = HOLD
```

This does not invalidate the active molecules. It prevents winner performance from being silently generalized to the complete generated class and prevents contradictory known counts from receiving an acceptance receipt.

## Independent-unit and replication boundary

The study reports activity in multiple biological systems, but the independent biological unit and effective biological N are not reconstructed in this preview record.

Cell measurements, targets, variants, and technical measurements must not silently become independent biological replications.

```text
INDEPENDENT_BIOLOGICAL_N = unresolved
INDEPENDENT_REPLICATION = not_assessed
```

Established independent replication would require all of the following:

- a registered external evidence object;
- evidence kind `independent_replication`;
- artifact kind `independent_replication_record`;
- F5 authority;
- a frozen artifact digest;
- unrelated-laboratory identity;
- independent materials;
- an accepted replication unit;
- exact references shared by the evidence object, replication status, and replication claim.

Peer review and multi-system testing do not themselves establish unrelated-laboratory replication. A risk-assessment artifact cannot mint replication authority merely by being labeled F5.

## Platform-generalization boundary

One independent reproduction would still not prove that a platform generalizes broadly. A supported platform claim must carry F5 external evidence whose kind, endpoint, and artifact class agree and whose combined coverage includes at least two distinct entries in **every** claimed dimension:

- target classes;
- laboratories;
- delivery systems;
- organisms;
- populations.

The SynTnpB reference record contains no such platform evidence and therefore keeps platform generalization `not_established`.

## Assay-semantic and risk-specific evidence boundary

Endpoint labels are not accepted as free-form authority.

- A cryo-EM structural observation must expose exactly the `structural_characterization` endpoint.
- Cellular activity assays may expose only bounded molecular-activity or named-comparator endpoints.
- Structural and activity assays cannot be relabeled as delivery, toxicity, immunogenicity, durability, off-target, or ecological-safety evidence.
- Established risk dimensions must resolve to external evidence objects of kind `risk_assessment` whose artifact kind is `risk_assessment_record` and whose endpoint explicitly matches the risk.

Every risk dimension is mandatory, but presence in the matrix is not evidence of safety.

Minimum preview.4 authority:

| Risk dimension | Minimum authority for `established` |
|---|---:|
| Specificity / off-target | F3 |
| Delivery | F4 |
| Immunogenicity | F4 |
| Toxicity | F4 |
| Durability | F4 |
| Ecological safety | F5 |

A cryo-EM structure cannot establish delivery or toxicity. A molecular-activity assay cannot establish immunogenicity or ecological safety. All six dimensions remain `not_established` in this case.

## Claim firewall

### Supported with limits

- The peer-reviewed publication reports active divergent TnpB variants after human laboratory construction and screening.
- It reports that some selected variants retained or exceeded the named study wild-type TnpB comparator in bounded cellular contexts.
- The deposited structure `9YYG` supports structural characterization of a selected active divergent variant.

### Not established

- reliable generalization across targets, laboratories, delivery platforms, organisms, and populations;
- comprehensive specificity or off-target performance;
- delivery performance;
- in-vivo efficacy;
- toxicity, immunogenicity, durability, and clinical safety;
- therapeutic efficacy;
- agricultural field performance or ecological safety;
- independent replication.

### Blocked

- “AI created a universally superior CRISPR”;
- “SynTnpB beats Cas9 and Cas12 generally”;
- “human-cell activity proves clinical readiness”;
- “plant-cell activity proves agricultural deployment readiness”;
- “structural contacts prove safety”;
- “the AI performed the research autonomously”;
- any claim that this repository authorizes synthesis, testing, deployment, treatment, or field use.

## Executable regression boundary

The exact-head workflow generates mutation cases from the accepted reference record rather than relying on a manually maintained fixture list. Its frozen 27-case manifest currently proves fail-closed behavior for 25 negative paths:

1. protected claim promoted to supported;
2. mismatched comparator;
3. claim comparator scope widened beyond the named comparator class;
4. comparator-only activity relabeled as designed-candidate evidence;
5. structured predicate relabeling;
6. ordinary publication reporting mislabeled F3;
7. replication below F5;
8. invented replication reference;
9. platform evidence with insufficient dimensional coverage;
10. whitespace-only platform coverage values;
11. platform support without established independent-replication state;
12. unreconciled complete candidate denominator;
13. risk status supported by the wrong evidence endpoint;
14. F5 risk evidence with whitespace-only laboratory and replication-unit identity;
15. mandatory risk dimensions marked not applicable;
16. positive mechanism state without its supported F4 structural evidence;
17. supported F4 structural evidence paired with a negative mechanism state;
18. supported selected-candidate claims with zero selected candidates;
19. a structural assay relabeled as delivery evidence;
20. impossible known counts inside a partial denominator;
21. an F5 artifact kind that contradicts the declared external evidence kind;
22. a nonexact positive selection after a known zero upstream count;
23. retained activity mislabeled with a superiority endpoint;
24. bounded superiority supported only by unselected designed candidates;
25. a computed F4 artifact self-labeled as laboratory confirmation.

Two positive compatibility cases separately prove acceptance of a digested F3
specificity-risk artifact and a directly reported F4 delivery-risk confirmation.

The acceptance receipt is created only after the positive audit and the complete mutation suite succeed. It hashes every audit record included in the positive result.

## Why this is a flagship BioEvidence OS case

The first reference case audits a path from single-cell data to replication and causal claims. SynTnpB exercises a different path:

```text
AI proposal
  -> generated candidate space
  -> candidate-stage reconciliation
  -> selected winner
  -> reported functional activity
  -> deposited structure
  -> safety and application narrative
```

The central governance problem is not whether the discovery is real. It is preventing a bounded molecular result from becoming an unsupported claim about universal superiority, medicine, agriculture, safety, or autonomous AI science.

## Next valid action

Obtain and audit the full article and supplementary information to reconstruct:

- exact candidate denominators and stage transitions;
- comparator-by-target performance;
- independent biological units and replicate counts;
- executable or reproducibility artifacts capable of F3 classification;
- specificity and off-target evidence;
- selection criteria and frozen decision points;
- scope of structural characterization;
- risk-specific evidence;
- independently resolvable F5 replication candidates.

The next action remains literature, data, and provenance analysis only. No physical biological work is authorized.
