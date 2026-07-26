# SynTnpB 2026 — AI-designed nuclease claim audit

## Audit identity

- **Case:** `syntnpb-science-aed6123-2026`
- **Primary publication:** *Structure and evolution-guided design of minimal RNA-guided nucleases*
- **Journal:** *Science*
- **DOI:** `10.1126/science.aed6123`
- **Publication date:** 2026-07-16
- **Primary publication page:** https://www.science.org/doi/10.1126/science.aed6123
- **Preprint/abstract record:** https://pubmed.ncbi.nlm.nih.gov/41573840/
- **Structural record example:** https://www.rcsb.org/structure/9YYG
- **News claim under audit:** an iXBT report framed the work as a synthetic CRISPR that surpassed natural enzymes and opened medical and agricultural applications.

## System boundary

This is a computational and documentary evidence audit. It contains no protein or DNA sequence, physical protocol, delivery method, concentration, optimization recipe, or authorization for biological execution.

## What the study supports

The paper reports a hybrid design pipeline combining structure-guided inverse protein folding, evolution-informed residue constraints, and laboratory screening. The designed entities are proposed **protein amino-acid sequences**. Physical proteins and cellular evidence were produced by the research team, not autonomously by the model.

The bounded evidence supports the following statements:

1. The strategy generated divergent TnpB candidates that retained functional RNA-guided nuclease activity after laboratory construction and screening.
2. Some selected SynTnpB variants retained or exceeded the activity of the study's wild-type TnpB reference in reported bacterial, plant-cell, and human-cell test contexts.
3. Cryo-EM characterization of a selected divergent active variant identified reported stabilizing contacts at RNA and DNA interfaces.

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

Universal cross-editor superiority is blocked unless a study directly benchmarks representative editors across prespecified targets, systems, endpoints, and safety dimensions.

## Evidence ladder

| Layer | Current evidence | Allowed interpretation | Prohibited escalation |
|---|---|---|---|
| AI design | Inverse-folding proposals constrained by structure and evolution | The computational strategy proposed divergent TnpB sequences | “AI autonomously created the complete validated system” |
| Functional screening | Active candidates in reported cellular systems | Molecular editing activity exists in those test contexts | Universal platform superiority |
| Comparator performance | Some selected variants retained or exceeded wild-type TnpB activity | Bounded comparator superiority | Superiority over Cas9, Cas12, or all natural editors |
| Human-cell assay | Editing activity in a human-cell system | Human-cell molecular activity | Clinical safety or therapeutic efficacy |
| Plant-cell assay | Editing activity in a plant-cell system | Plant-cell molecular activity | Field readiness, ecological safety, or agricultural deployment |
| Cryo-EM | Structure of a selected divergent active variant | Structural contacts were observed | Complete causal mechanism, safety, or broad superiority |
| Publication | Peer-reviewed originating-collaboration report | The study passed journal review | Independent replication by an unrelated laboratory |

## Selection and denominator boundary

The public abstract and news summaries describe thousands of computational variants and high-throughput screening, but this preview audit does not reconstruct a complete candidate denominator.

Unresolved fields include:

- exact generated count;
- exact screened count across every stage;
- complete failed-candidate reporting;
- whether winner-selection rules were prespecified before observing all outcomes;
- target-by-target and system-by-system performance distributions;
- how strongly the selected cryo-EM variant represents the full designed library.

```text
SELECTION_BIAS_STATUS = HOLD
```

This does not invalidate the active molecules. It prevents winner performance from being silently generalized to the complete generated class.

## Independent-unit boundary

The study reports activity in multiple biological systems, but the independent biological unit and effective biological N are not reconstructed in this preview record.

Cell measurements, targets, variants, and technical measurements must not silently become independent biological replications.

```text
INDEPENDENT_BIOLOGICAL_N = unresolved
INDEPENDENT_REPLICATION = not_assessed
```

Peer review and multi-system testing do not themselves establish unrelated-laboratory replication.

## Claim firewall

### Supported with limits

- AI/evolution-guided sequence design produced active divergent TnpB variants after human laboratory construction and screening.
- Some selected SynTnpB variants retained or exceeded the study wild-type TnpB comparator in reported cellular tests.
- Cryo-EM of a selected active divergent variant revealed reported stabilizing interface contacts.

### Not established

- reliable generalization across targets, laboratories, delivery platforms, organisms, and populations;
- comprehensive specificity or off-target superiority;
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

## Why this is a flagship BioEvidence OS case

The first reference case audits a path from single-cell data to replication and causal claims. SynTnpB exercises a different path:

```text
AI proposal
  -> generated candidate space
  -> screening denominator
  -> selected winner
  -> functional activity
  -> structure
  -> application narrative
```

The central governance problem is not whether the discovery is real. It is preventing a bounded molecular result from becoming an unsupported claim about universal superiority, medicine, agriculture, or autonomous AI science.

## Next valid action

Obtain and audit the full article and supplementary information to reconstruct:

- exact candidate denominators and stage transitions;
- comparator-by-target performance;
- independent biological units and replicate counts;
- specificity and off-target evidence;
- selection criteria and frozen decision points;
- scope of structural characterization;
- independent replication candidates.

The next action remains literature, data, and provenance analysis only. No physical biological work is authorized.
