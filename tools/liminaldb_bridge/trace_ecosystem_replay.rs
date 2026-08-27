use std::{env, fs, path::PathBuf};

use anyhow::{anyhow, Context, Result};
use liminal_store::{
    sha256_ref, AuthorityState, CausalValidityState, ContinuityPosture, ExecutionState,
    ResponseIntegrityState, TransitionDimensions, TransitionEventInput, TransitionLinks,
    TransitionRecordKind, TrustworthyTransitionLedger,
};
use serde::Serialize;
use serde_json::Value;

const LIMINALDB_COMMIT: &str = "b8cf0528187c6d3fac3b28dbb9e90f1a2fb740e7";
const LEDGER_PROFILE: &str = "org.liminaldb.trustworthy-transition-ledger.v0.1";
const RECEIPT_SCHEMA: &str = "kairos.trace-ecosystem-receipt.v0.1";

#[derive(Serialize)]
struct ReplayReceipt {
    schema_version: &'static str,
    artifact_type: &'static str,
    liminaldb_commit: &'static str,
    source_receipt_sha256: String,
    transition_id: String,
    event_count_before_reopen: u64,
    event_count_after_reopen: u64,
    snapshot_digest: String,
    snapshot_event_count: u64,
    projection_count: usize,
    projection_equal_after_reopen: bool,
    final_authorization_ref: Option<String>,
    final_observation_refs: Vec<String>,
    final_response_integrity_ref: Option<String>,
    final_causal_audit_ref: Option<String>,
    final_continuity_snapshot_ref: Option<String>,
    final_dimensions: Option<TransitionDimensions>,
    final_side_effect_committed: bool,
    final_event_count: u64,
    final_event_hash: String,
    source_verdict: String,
    adds_scientific_verdict: bool,
    verdict: &'static str,
}

fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str> {
    value
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| anyhow!("missing string: {key}"))
}

fn object<'a>(value: &'a Value, key: &str) -> Result<&'a serde_json::Map<String, Value>> {
    value
        .get(key)
        .and_then(Value::as_object)
        .ok_or_else(|| anyhow!("missing object: {key}"))
}

fn dimensions(kind: &str) -> Option<TransitionDimensions> {
    if kind == "authorization" {
        return None;
    }
    Some(TransitionDimensions {
        authority: AuthorityState::Valid,
        execution: ExecutionState::ObservedExecuted,
        response_integrity: if matches!(kind, "response_integrity" | "causal_audit" | "continuity_snapshot") {
            ResponseIntegrityState::Verified
        } else {
            ResponseIntegrityState::NotEvaluated
        },
        causal_validity: CausalValidityState::NotEvaluated,
        continuity_posture: if matches!(kind, "causal_audit" | "continuity_snapshot") {
            ContinuityPosture::ReportOnly
        } else {
            ContinuityPosture::NotEvaluated
        },
    })
}

fn kind(value: &str) -> Result<TransitionRecordKind> {
    match value {
        "authorization" => Ok(TransitionRecordKind::Authorization),
        "observation" => Ok(TransitionRecordKind::Observation),
        "response_integrity" => Ok(TransitionRecordKind::ResponseIntegrity),
        "causal_audit" => Ok(TransitionRecordKind::CausalAudit),
        "continuity_snapshot" => Ok(TransitionRecordKind::ContinuitySnapshot),
        other => Err(anyhow!("unexpected record type: {other}")),
    }
}

fn main() -> Result<()> {
    let mut args = env::args().skip(1);
    let source_path = PathBuf::from(args.next().context("source receipt argument missing")?);
    let ledger_root = PathBuf::from(args.next().context("ledger root argument missing")?);
    let output_path = PathBuf::from(args.next().context("output receipt argument missing")?);
    if args.next().is_some() {
        return Err(anyhow!("unexpected extra arguments"));
    }

    let source_bytes = fs::read(&source_path).context("read TRACE ecosystem receipt")?;
    let source: Value = serde_json::from_slice(&source_bytes).context("parse TRACE ecosystem receipt")?;
    if text(&source, "schema")? != RECEIPT_SCHEMA {
        return Err(anyhow!("unsupported source receipt schema"));
    }

    let authority = object(&source, "authority")?;
    if authority.get("classification").and_then(Value::as_str) != Some("RESEARCH_ONLY") {
        return Err(anyhow!("source receipt is not RESEARCH_ONLY"));
    }
    for key in [
        "scientific_truth_authorized",
        "causal_authorization",
        "experiment_authorization",
        "clinical_authorization",
        "ancestry_identity_authorization",
        "deployment_authorization",
        "merge_authorization",
    ] {
        if authority.get(key).and_then(Value::as_bool) != Some(false) {
            return Err(anyhow!("authority escalation at {key}"));
        }
    }

    let liminal = source
        .get("liminaldb_projection")
        .ok_or_else(|| anyhow!("missing liminaldb_projection"))?;
    if text(liminal, "profile")? != LEDGER_PROFILE
        || text(liminal, "conformance")? != "DOCUMENTARY_PROJECTION_NOT_RUST_REPLAY"
        || text(liminal, "supersession_relation")? != "ROOT"
        || liminal.get("local_projection_replay_equal").and_then(Value::as_bool) != Some(true)
    {
        return Err(anyhow!("documentary projection boundary changed"));
    }

    let projection = liminal
        .get("projection")
        .ok_or_else(|| anyhow!("missing projection"))?;
    if text(projection, "authority")? != "VALID_RESEARCH_ONLY"
        || text(projection, "execution")? != "OBSERVED_EXECUTED"
        || text(projection, "response_integrity")? != "VERIFIED"
        || text(projection, "causal_validity")? != "RANKED_NOT_IDENTIFIED"
        || text(projection, "continuity_posture")? != "REPORT_ONLY"
        || text(projection, "source_verdict")? != "ACCEPT_WITH_LIMITS"
        || projection.get("side_effect_committed").and_then(Value::as_bool) != Some(false)
        || projection.get("adds_scientific_verdict").and_then(Value::as_bool) != Some(false)
    {
        return Err(anyhow!("final projection exceeded the source boundary"));
    }

    let transition_id = text(liminal, "transition_id")?.to_owned();
    let source_records = liminal
        .get("records")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow!("missing records"))?;
    let expected = [
        "authorization",
        "observation",
        "response_integrity",
        "causal_audit",
        "continuity_snapshot",
    ];
    if source_records.len() != expected.len() {
        return Err(anyhow!("expected exactly five records"));
    }

    let refs: Vec<String> = source_records
        .iter()
        .enumerate()
        .map(|(index, record)| {
            let record_type = text(record, "record_type")?;
            if record_type != expected[index] {
                return Err(anyhow!("record order changed at index {index}"));
            }
            if record.get("sequence").and_then(Value::as_u64) != Some((index + 1) as u64) {
                return Err(anyhow!("record sequence changed at index {index}"));
            }
            Ok(sha256_ref(
                format!(
                    "{}|{}|{}|{}",
                    transition_id,
                    record_type,
                    text(record, "record_ref")?,
                    text(record, "event_hash")?
                )
                .as_bytes(),
            ))
        })
        .collect::<Result<_>>()?;

    if ledger_root.exists() {
        fs::remove_dir_all(&ledger_root).context("remove stale temporary ledger")?;
    }
    fs::create_dir_all(&ledger_root).context("create temporary ledger")?;
    let mut ledger = TrustworthyTransitionLedger::open(&ledger_root).context("open ledger")?;

    for (index, record) in source_records.iter().enumerate() {
        let record_type = expected[index];
        let payload = record.get("payload").ok_or_else(|| anyhow!("missing payload"))?;
        let payload_digest = sha256_ref(
            serde_json::to_vec(&serde_json::json!({
                "payload": payload,
                "source_payload_digest": text(record, "payload_digest")?,
                "source_event_hash": text(record, "event_hash")?,
            }))?
            .as_slice(),
        );
        let links = match index {
            0 => TransitionLinks::default(),
            1 => TransitionLinks {
                authorization_ref: Some(refs[0].clone()),
                ..TransitionLinks::default()
            },
            2 => TransitionLinks {
                authorization_ref: Some(refs[0].clone()),
                observation_refs: vec![refs[1].clone()],
                ..TransitionLinks::default()
            },
            3 => TransitionLinks {
                authorization_ref: Some(refs[0].clone()),
                observation_refs: vec![refs[1].clone()],
                response_integrity_ref: Some(refs[2].clone()),
                ..TransitionLinks::default()
            },
            4 => TransitionLinks {
                authorization_ref: Some(refs[0].clone()),
                observation_refs: vec![refs[1].clone()],
                response_integrity_ref: Some(refs[2].clone()),
                causal_audit_ref: Some(refs[3].clone()),
                previous_continuity_ref: None,
            },
            _ => unreachable!(),
        };
        ledger.append(TransitionEventInput {
            transition_id: transition_id.clone(),
            subject_id: "kairos:trace-evidence-package-pr55".into(),
            kind: kind(record_type)?,
            record_ref: refs[index].clone(),
            payload_digest,
            links,
            dimensions: dimensions(record_type),
            side_effect_committed: Some(false),
            captured_at_ms: (index + 1) as u64,
        })?;
    }

    let before = ledger
        .projection(&transition_id)
        .cloned()
        .context("projection missing before snapshot")?;
    let event_count_before = ledger.event_count();
    let snapshot = ledger.write_snapshot(6).context("write snapshot")?;
    drop(ledger);

    let reopened = TrustworthyTransitionLedger::open(&ledger_root).context("reopen ledger")?;
    let after = reopened
        .projection(&transition_id)
        .cloned()
        .context("projection missing after reopen")?;
    if before != after {
        return Err(anyhow!("projection changed after snapshot-assisted reopen"));
    }
    if after.side_effect_committed || after.event_count != 5 {
        return Err(anyhow!("replayed projection crossed the report-only boundary"));
    }
    if after.authorization_ref.as_ref() != Some(&refs[0])
        || after.observation_refs != vec![refs[1].clone()]
        || after.response_integrity_ref.as_ref() != Some(&refs[2])
        || after.causal_audit_ref.as_ref() != Some(&refs[3])
        || after.continuity_snapshot_ref.as_ref() != Some(&refs[4])
    {
        return Err(anyhow!("replayed projection references differ from the source chain"));
    }

    let receipt = ReplayReceipt {
        schema_version: "0.1.0",
        artifact_type: "trace_liminaldb_rust_replay_receipt",
        liminaldb_commit: LIMINALDB_COMMIT,
        source_receipt_sha256: sha256_ref(&source_bytes),
        transition_id,
        event_count_before_reopen: event_count_before,
        event_count_after_reopen: reopened.event_count(),
        snapshot_digest: snapshot.snapshot_digest().to_owned(),
        snapshot_event_count: snapshot.event_count(),
        projection_count: snapshot.projection_count(),
        projection_equal_after_reopen: true,
        final_authorization_ref: after.authorization_ref,
        final_observation_refs: after.observation_refs,
        final_response_integrity_ref: after.response_integrity_ref,
        final_causal_audit_ref: after.causal_audit_ref,
        final_continuity_snapshot_ref: after.continuity_snapshot_ref,
        final_dimensions: after.dimensions,
        final_side_effect_committed: after.side_effect_committed,
        final_event_count: after.event_count,
        final_event_hash: after.last_event_hash,
        source_verdict: "ACCEPT_WITH_LIMITS".into(),
        adds_scientific_verdict: false,
        verdict: "RUST_REPLAY_RECOVERED_REPORT_ONLY",
    };
    if let Some(parent) = output_path.parent() {
        fs::create_dir_all(parent).context("create output directory")?;
    }
    fs::write(&output_path, serde_json::to_vec_pretty(&receipt)?)?;
    println!("{}", serde_json::to_string(&receipt)?);
    Ok(())
}
