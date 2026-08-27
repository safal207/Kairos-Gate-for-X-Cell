"""Fail-closed transition-network analysis for Kairos Gate.

The engine evaluates the support structure of a proposed path. It does not
validate biological truth, assign taxonomy, establish causality, authorize
experiments, or convert model confidence into action authority.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


class TransitionGraphError(ValueError):
    """Raised when a transition graph violates structural invariants."""


EVIDENCE_STATUS_WEIGHT = {
    "missing_evidence": 0.00,
    "contradicted": 0.00,
    "computational_inference": 0.45,
    "author_reported": 0.50,
    "direct_observation": 0.70,
    "independently_replicated": 0.90,
}

CLAIM_LEVEL = {
    "hypothesis": 0,
    "association": 1,
    "mechanism": 2,
    "causal": 3,
    "authorization": 4,
}

STATUS_MAX_CLAIM = {
    "missing_evidence": 0,
    "contradicted": 0,
    "computational_inference": 1,
    "author_reported": 1,
    "direct_observation": 2,
    "independently_replicated": 2,
}


@dataclass(frozen=True)
class TransitionScore:
    """Transparent score for ranking candidate transitions, not probability."""

    transition_id: str
    score: float
    supporting_evidence: int
    independent_evidence: int
    contradictory_evidence: int
    missing_evidence_refs: tuple[str, ...]


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TransitionGraphError(f"{label} must be an object")
    return value


def _require_sequence(value: Any, label: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TransitionGraphError(f"{label} must be an array")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TransitionGraphError(f"{label} must be a non-empty string")
    return value


def _finite_score(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TransitionGraphError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise TransitionGraphError(f"{label} must be finite and between 0 and 1")
    return result


def _time_window(value: Any, label: str) -> tuple[float, float, str]:
    window = _require_mapping(value, label)
    start = window.get("start")
    end = window.get("end")
    if isinstance(start, bool) or not isinstance(start, (int, float)):
        raise TransitionGraphError(f"{label}.start must be numeric")
    if isinstance(end, bool) or not isinstance(end, (int, float)):
        raise TransitionGraphError(f"{label}.end must be numeric")
    start_f = float(start)
    end_f = float(end)
    if not math.isfinite(start_f) or not math.isfinite(end_f):
        raise TransitionGraphError(f"{label} bounds must be finite")
    if start_f > end_f:
        raise TransitionGraphError(f"{label}.start must be <= end")
    unit = _require_text(window.get("unit"), f"{label}.unit")
    return start_f, end_f, unit


def _overlap(left: tuple[float, float, str], right: tuple[float, float, str]) -> bool:
    if left[2] != right[2]:
        return False
    return max(left[0], right[0]) <= min(left[1], right[1])


def _index_by_id(items: Sequence[Any], label: str) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for position, raw in enumerate(items):
        item = _require_mapping(raw, f"{label}[{position}]")
        item_id = _require_text(item.get("id"), f"{label}[{position}].id")
        if item_id in indexed:
            raise TransitionGraphError(f"duplicate {label} id: {item_id}")
        indexed[item_id] = item
    return indexed


def validate_graph(graph: Mapping[str, Any]) -> None:
    """Validate graph structure and all cross-references fail-closed."""
    _require_text(graph.get("graph_id"), "graph_id")
    _require_text(graph.get("schema_version"), "schema_version")
    _require_text(graph.get("domain"), "domain")

    states = _index_by_id(_require_sequence(graph.get("states"), "states"), "states")
    evidence = _index_by_id(
        _require_sequence(graph.get("evidence"), "evidence"), "evidence"
    )
    transitions = _index_by_id(
        _require_sequence(graph.get("transitions"), "transitions"), "transitions"
    )

    if not states:
        raise TransitionGraphError("graph must contain at least one state")
    if not transitions:
        raise TransitionGraphError("graph must contain at least one transition")

    for state_id, state in states.items():
        _require_text(state.get("type"), f"state {state_id}.type")
        _require_text(state.get("label"), f"state {state_id}.label")
        _time_window(state.get("time_window"), f"state {state_id}.time_window")
        _finite_score(state.get("uncertainty"), f"state {state_id}.uncertainty")
        state_refs = _require_sequence(
            state.get("evidence_refs", []), f"state {state_id}.evidence_refs"
        )
        normalized_state_refs = [
            _require_text(ref, f"state {state_id}.evidence_refs[{position}]")
            for position, ref in enumerate(state_refs)
        ]
        if len(normalized_state_refs) != len(set(normalized_state_refs)):
            raise TransitionGraphError(
                f"state {state_id}.evidence_refs must not contain duplicates"
            )
        for ref in normalized_state_refs:
            if ref not in evidence:
                raise TransitionGraphError(
                    f"state {state_id} references missing evidence: {ref}"
                )

    for evidence_id, item in evidence.items():
        status = _require_text(item.get("status"), f"evidence {evidence_id}.status")
        if status not in EVIDENCE_STATUS_WEIGHT:
            raise TransitionGraphError(
                f"evidence {evidence_id} has unsupported status: {status}"
            )
        _require_text(item.get("kind"), f"evidence {evidence_id}.kind")
        _require_text(item.get("source"), f"evidence {evidence_id}.source")
        _finite_score(item.get("strength"), f"evidence {evidence_id}.strength")
        if not isinstance(item.get("independent"), bool):
            raise TransitionGraphError(
                f"evidence {evidence_id}.independent must be boolean"
            )
        if not isinstance(item.get("causal_design", False), bool):
            raise TransitionGraphError(
                f"evidence {evidence_id}.causal_design must be boolean"
            )
        for relation in ("supports", "contradicts"):
            raw_targets = _require_sequence(
                item.get(relation, []), f"evidence {evidence_id}.{relation}"
            )
            targets = [
                _require_text(
                    target,
                    f"evidence {evidence_id}.{relation}[{position}]",
                )
                for position, target in enumerate(raw_targets)
            ]
            if len(targets) != len(set(targets)):
                raise TransitionGraphError(
                    f"evidence {evidence_id}.{relation} must not contain duplicates"
                )
            for target in targets:
                if target not in transitions:
                    raise TransitionGraphError(
                        f"evidence {evidence_id}.{relation} references missing "
                        f"transition: {target}"
                    )

    for transition_id, transition in transitions.items():
        source_id = _require_text(
            transition.get("from_state"), f"transition {transition_id}.from_state"
        )
        target_id = _require_text(
            transition.get("to_state"), f"transition {transition_id}.to_state"
        )
        if source_id not in states:
            raise TransitionGraphError(
                f"transition {transition_id} references missing source state: {source_id}"
            )
        if target_id not in states:
            raise TransitionGraphError(
                f"transition {transition_id} references missing target state: {target_id}"
            )
        if source_id == target_id:
            raise TransitionGraphError(
                f"transition {transition_id} cannot be a self-transition"
            )
        _require_text(
            transition.get("mechanism"), f"transition {transition_id}.mechanism"
        )
        transition_window = _time_window(
            transition.get("time_window"), f"transition {transition_id}.time_window"
        )
        source_window = _time_window(
            states[source_id].get("time_window"), f"state {source_id}.time_window"
        )
        target_window = _time_window(
            states[target_id].get("time_window"), f"state {target_id}.time_window"
        )
        if (
            transition_window[2] != source_window[2]
            or transition_window[2] != target_window[2]
        ):
            raise TransitionGraphError(
                f"transition {transition_id} and endpoint states must use the same time unit"
            )
        _finite_score(
            transition.get("confidence"), f"transition {transition_id}.confidence"
        )
        status = _require_text(
            transition.get("status"), f"transition {transition_id}.status"
        )
        if status not in EVIDENCE_STATUS_WEIGHT:
            raise TransitionGraphError(
                f"transition {transition_id} has unsupported status: {status}"
            )
        refs = _require_sequence(
            transition.get("evidence_refs", []),
            f"transition {transition_id}.evidence_refs",
        )
        normalized_refs = [
            _require_text(
                ref, f"transition {transition_id}.evidence_refs[{position}]"
            )
            for position, ref in enumerate(refs)
        ]
        if len(normalized_refs) != len(set(normalized_refs)):
            raise TransitionGraphError(
                f"transition {transition_id}.evidence_refs must not contain duplicates"
            )
        for ref in normalized_refs:
            if ref not in evidence:
                raise TransitionGraphError(
                    f"transition {transition_id} references missing evidence: {ref}"
                )
        claim = _require_mapping(
            transition.get("claim", {}), f"transition {transition_id}.claim"
        )
        _require_text(claim.get("text"), f"transition {transition_id}.claim.text")
        level = _require_text(
            claim.get("level"), f"transition {transition_id}.claim.level"
        )
        if level not in CLAIM_LEVEL:
            raise TransitionGraphError(
                f"transition {transition_id} has unsupported claim level: {level}"
            )


def temporal_conflicts(graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return transitions whose time window cannot coexist with endpoint states."""
    validate_graph(graph)
    states = {item["id"]: item for item in graph["states"]}
    conflicts: list[dict[str, Any]] = []
    for transition in graph["transitions"]:
        transition_window = _time_window(
            transition["time_window"], f"transition {transition['id']}.time_window"
        )
        source_window = _time_window(
            states[transition["from_state"]]["time_window"],
            f"state {transition['from_state']}.time_window",
        )
        target_window = _time_window(
            states[transition["to_state"]]["time_window"],
            f"state {transition['to_state']}.time_window",
        )
        reasons = []
        if not _overlap(transition_window, source_window):
            reasons.append("NO_SOURCE_STATE_OVERLAP")
        if not _overlap(transition_window, target_window):
            reasons.append("NO_TARGET_STATE_OVERLAP")
        if reasons:
            conflicts.append({"transition_id": transition["id"], "reasons": reasons})
    return conflicts


def causal_gaps(graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return declared intermediate steps that lack observed support."""
    validate_graph(graph)
    gaps: list[dict[str, Any]] = []
    for transition in graph["transitions"]:
        required = {
            _require_text(value, "required_intermediate")
            for value in _require_sequence(
                transition.get("required_intermediates", []),
                f"transition {transition['id']}.required_intermediates",
            )
        }
        observed = {
            _require_text(value, "observed_intermediate")
            for value in _require_sequence(
                transition.get("observed_intermediates", []),
                f"transition {transition['id']}.observed_intermediates",
            )
        }
        missing = sorted(required - observed)
        if missing:
            gaps.append(
                {
                    "transition_id": transition["id"],
                    "missing_intermediates": missing,
                    "status": "CAUSAL_GAP",
                }
            )
    return gaps


def _allowed_claim_level(
    transition: Mapping[str, Any], evidence_index: Mapping[str, Mapping[str, Any]]
) -> int:
    allowed = STATUS_MAX_CLAIM[transition["status"]]
    refs = transition.get("evidence_refs", [])
    causal_support = any(
        evidence_index[ref].get("causal_design") is True
        and evidence_index[ref]["status"] in {"direct_observation", "independently_replicated"}
        for ref in refs
    )
    if causal_support:
        allowed = max(allowed, CLAIM_LEVEL["causal"])
    if any(evidence_index[ref]["status"] == "contradicted" for ref in refs):
        allowed = min(allowed, CLAIM_LEVEL["association"])
    return min(allowed, CLAIM_LEVEL["causal"])


def claim_firewall(graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Block claims that exceed their strongest admissible evidence level."""
    validate_graph(graph)
    evidence_index = {item["id"]: item for item in graph["evidence"]}
    violations: list[dict[str, Any]] = []
    for transition in graph["transitions"]:
        requested_name = transition["claim"]["level"]
        requested = CLAIM_LEVEL[requested_name]
        allowed = _allowed_claim_level(transition, evidence_index)
        if requested > allowed:
            allowed_name = max(
                (name for name, value in CLAIM_LEVEL.items() if value == allowed),
                key=len,
            )
            violations.append(
                {
                    "transition_id": transition["id"],
                    "claim_level": requested_name,
                    "allowed_level": allowed_name,
                    "status": "OVERCLAIM_BLOCKED",
                }
            )
    return violations


def rank_transitions(graph: Mapping[str, Any]) -> list[TransitionScore]:
    """Rank transitions by transparent evidence support, not truth probability."""
    validate_graph(graph)
    evidence_index = {item["id"]: item for item in graph["evidence"]}
    ranked: list[TransitionScore] = []
    for transition in graph["transitions"]:
        refs = list(transition.get("evidence_refs", []))
        support_total = 0.0
        independent = 0
        contradictions = 0
        for ref in refs:
            item = evidence_index[ref]
            status = item["status"]
            if status == "contradicted":
                contradictions += 1
                continue
            if item["independent"]:
                independent += 1
            support_total += EVIDENCE_STATUS_WEIGHT[status] * float(item["strength"])
        evidence_component = support_total / max(len(refs), 1)
        independence_bonus = min(independent * 0.05, 0.15)
        contradiction_penalty = min(contradictions * 0.30, 0.60)
        status_component = EVIDENCE_STATUS_WEIGHT[transition["status"]]
        declared_confidence = float(transition["confidence"])
        score = (
            0.45 * evidence_component
            + 0.30 * status_component
            + 0.25 * declared_confidence
            + independence_bonus
            - contradiction_penalty
        )
        ranked.append(
            TransitionScore(
                transition_id=transition["id"],
                score=round(max(0.0, min(1.0, score)), 6),
                supporting_evidence=len(refs) - contradictions,
                independent_evidence=independent,
                contradictory_evidence=contradictions,
                missing_evidence_refs=(),
            )
        )
    return sorted(ranked, key=lambda item: (-item.score, item.transition_id))


def support_profile(graph: Mapping[str, Any]) -> dict[str, float]:
    """Summarize transition statuses as shares of the declared graph path."""
    validate_graph(graph)
    counts = Counter(transition["status"] for transition in graph["transitions"])
    total = len(graph["transitions"])
    return {
        status: round(count / total, 6)
        for status, count in sorted(counts.items())
    }


def analyze_transition_network(graph: Mapping[str, Any]) -> dict[str, Any]:
    """Run all v0.1 checks and return a deterministic research-only report."""
    validate_graph(graph)
    temporal = temporal_conflicts(graph)
    gaps = causal_gaps(graph)
    overclaims = claim_firewall(graph)
    ranking = rank_transitions(graph)
    blocked = bool(temporal or overclaims)
    return {
        "schema": "kairos.transition-network-analysis.v0.1",
        "graph_id": graph["graph_id"],
        "verdict": "BLOCK" if blocked else "ACCEPT_WITH_LIMITS",
        "support_profile": support_profile(graph),
        "temporal_conflicts": temporal,
        "causal_gaps": gaps,
        "claim_firewall": overclaims,
        "transition_ranking": [
            {
                "transition_id": item.transition_id,
                "score": item.score,
                "supporting_evidence": item.supporting_evidence,
                "independent_evidence": item.independent_evidence,
                "contradictory_evidence": item.contradictory_evidence,
            }
            for item in ranking
        ],
        "authority": {
            "classification": "RESEARCH_ONLY",
            "truth_probability": False,
            "causal_authorization": False,
            "experiment_authorization": False,
            "clinical_authorization": False,
            "merge_authorization": False,
        },
    }
