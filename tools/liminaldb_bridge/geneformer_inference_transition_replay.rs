use std::env;
use std::fs;
use std::path::PathBuf;

use anyhow::{anyhow, Context, Result};
use liminal_store::{
    AuthorityState, CausalValidityState, ContinuityPosture, ExecutionState,
    ResponseIntegrityState, TransitionDimensions, TransitionEventInput, TransitionLinks,
    TransitionRecordKind, TrustworthyTransitionLedger,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

const EXPECTED_LIMINALDB_COMMIT: &str = "ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d";
const EXPECTED_PROFILE: &str = "org.liminaldb.trustworthy-transition-ledger.v0.1";
const EXPECTED_PREDECESSOR_TRANSITION: &str = "gse184241-geneformer-runtime-preflight-v0-1";
const EXPECTED_PREDECESSOR_AUTHORIZATION: &str = "sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665";

#[derive(Debug, Deserialize)]
struct Bundle {
    schema_version: String,
    bridge_profile: String,
    liminaldb_pin: LiminalDbPin,
    transition_id: String,
    subject_id: String,
    action: String,
    supersession: Supersession,
    records: Vec<Record>,
    storage_boundary: StorageBoundary,
}

#[derive(Debug, Deserialize)]
struct LiminalDbPin {
    repository: String,
    commit: String,
    event_schema: String,
    ledger_profile: String,
}

#[derive(Debug, Deserialize)]
struct Supersession {
    relation: String,
    predecessor_transition_id: Option<String>,
    predecessor_authorization_ref: Option<String>,
}

#[derive(Debug, Deserialize)]
struct StorageBoundary {
    temporary_ledger_only: bool,
    production_write: bool,
    external_submission: bool,
    deployment: bool,
    merge: bool,
}

#[derive(Debug, Deserialize)]
struct Record {
    kind: String,
    record_ref: String,
    payload_digest: String,
    links: RecordLinks,
    dimensions: Option<RecordDimensions>,
    side_effect_committed: bool,
    captured_at_ms: u64,
}

#[derive(Debug, Deserialize)]
struct RecordLinks {
    authorization_ref: Option<String>,
    observation_refs: Vec<String>,
    response_integrity_ref: Option<String>,
    causal_audit_ref: Option<String>,
    previous_continuity_ref: Option<String>,
}

#[derive(Debug, Deserialize)]
struct RecordDimensions {
    authority: String,
    execution: String,
    response_integrity: String,
    causal_validity: String,
    continuity_posture: String,
}

#[derive(Debug, Serialize)]
struct Receipt {
    schema_version: &'static str,
    artifact_type: &'static str,
    liminaldb_commit: &'static str,
    bundle_sha256: String,
    transition_id: String,
    subject_id: String,
    supersession_relation: String,
    predecessor_transition_id: Option<String>,
    predecessor_authorization_ref: Option<String>,
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
    verdict: &'static str,
}

fn record_kind(value: &str) -> Result<TransitionRecordKind> {
    match value {
        "authorization" => Ok(TransitionRecordKind::Authorization),
        "observation" => Ok(TransitionRecordKind::Observation),
        "response_integrity" => Ok(TransitionRecordKind::ResponseIntegrity),
        "causal_audit" => Ok(TransitionRecordKind::CausalAudit),
        "continuity_snapshot" => Ok(TransitionRecordKind::ContinuitySnapshot),
        other => Err(anyhow!("unknown record kind: {other}")),
    }
}

fn authority(value: &str) -> Result<AuthorityState> {
    match value {
        "VALID" => Ok(AuthorityState::Valid),
        "DENIED" => Ok(AuthorityState::Denied),
        "PENDING" => Ok(AuthorityState::Pending),
        "EXPIRED" => Ok(AuthorityState::Expired),
        "EXPIRED_AT_REPORT" => Ok(AuthorityState::ExpiredAtReport),
        "CONSUMED" => Ok(AuthorityState::Consumed),
        "REVALIDATION_REQUIRED" => Ok(AuthorityState::RevalidationRequired),
        "NOT_EVALUATED" => Ok(AuthorityState::NotEvaluated),
        "UNKNOWN" => Ok(AuthorityState::Unknown),
        other => Err(anyhow!("unknown authority state: {other}")),
    }
}

fn execution(value: &str) -> Result<ExecutionState> {
    match value {
        "NOT_OBSERVED" => Ok(ExecutionState::NotObserved),
        "OBSERVED_EXECUTED" => Ok(ExecutionState::ObservedExecuted),
        "OBSERVED_BLOCKED" => Ok(ExecutionState::ObservedBlocked),
        "OBSERVED_ERRORED" => Ok(ExecutionState::ObservedErrored),
        "OBSERVED_OTHER" => Ok(ExecutionState::ObservedOther),
        other => Err(anyhow!("unknown execution state: {other}")),
    }
}

fn response_integrity(value: &str) -> Result<ResponseIntegrityState> {
    match value {
        "VERIFIED" => Ok(ResponseIntegrityState::Verified),
        "FAILED" => Ok(ResponseIntegrityState::Failed),
        "PARTIAL" => Ok(ResponseIntegrityState::Partial),
        "NOT_EVALUATED" => Ok(ResponseIntegrityState::NotEvaluated),
        "UNKNOWN" => Ok(ResponseIntegrityState::Unknown),
        other => Err(anyhow!("unknown response-integrity state: {other}")),
    }
}

fn causal_validity(value: &str) -> Result<CausalValidityState> {
    match value {
        "VALID" => Ok(CausalValidityState::Valid),
        "INVALID" => Ok(CausalValidityState::Invalid),
        "NOT_EVALUATED" => Ok(CausalValidityState::NotEvaluated),
        "UNKNOWN" => Ok(CausalValidityState::Unknown),
        other => Err(anyhow!("unknown causal-validity state: {other}")),
    }
}

fn continuity_posture(value: &str) -> Result<ContinuityPosture> {
    match value {
        "CONTINUE_SIDE_EFFECT" => Ok(ContinuityPosture::ContinueSideEffect),
        "RETRY_SIDE_EFFECT" => Ok(ContinuityPosture::RetrySideEffect),
        "REPORT_ONLY" => Ok(ContinuityPosture::ReportOnly),
        "REMEDIATE_RESPONSE" => Ok(ContinuityPosture::RemediateResponse),
        "REVALIDATE" => Ok(ContinuityPosture::Revalidate),
        "BLOCKED" => Ok(ContinuityPosture::Blocked),
        "ALREADY_CONSUMED" => Ok(ContinuityPosture::AlreadyConsumed),
        "NOT_EVALUATED" => Ok(ContinuityPosture::NotEvaluated),
        other => Err(anyhow!("unknown continuity posture: {other}")),
    }
}

fn convert_dimensions(value: Option<RecordDimensions>) -> Result<Option<TransitionDimensions>> {
    value
        .map(|dimensions| {
            Ok(TransitionDimensions {
                authority: authority(&dimensions.authority)?,
                execution: execution(&dimensions.execution)?,
                response_integrity: response_integrity(&dimensions.response_integrity)?,
                causal_validity: causal_validity(&dimensions.causal_validity)?,
                continuity_posture: continuity_posture(&dimensions.continuity_posture)?,
            })
        })
        .transpose()
}

fn sha256_ref(bytes: &[u8]) -> String {
    let digest = Sha256::digest(bytes);
    format!("sha256:{digest:x}")
}

fn main() -> Result<()> {
    let mut args = env::args().skip(1);
    let bundle_path = PathBuf::from(args.next().context("bundle path argument missing")?);
    let ledger_root = PathBuf::from(args.next().context("ledger root argument missing")?);
    let receipt_path = PathBuf::from(args.next().context("receipt path argument missing")?);
    if args.next().is_some() {
        return Err(anyhow!("unexpected extra arguments"));
    }
    let bundle_bytes = fs::read(&bundle_path).with_context(|| format!("read {}", bundle_path.display()))?;
    let bundle: Bundle = serde_json::from_slice(&bundle_bytes).context("parse inference bundle")?;
    if bundle.schema_version != "0.1.0"
        || bundle.bridge_profile != "org.kairos-gate.liminaldb-geneformer-inference-bridge.v0.1"
        || bundle.liminaldb_pin.repository != "safal207/LiminalDB"
        || bundle.liminaldb_pin.commit != EXPECTED_LIMINALDB_COMMIT
        || bundle.liminaldb_pin.event_schema != "liminaldb.trustworthy-transition-event.v0.1"
        || bundle.liminaldb_pin.ledger_profile != EXPECTED_PROFILE
    {
        return Err(anyhow!("bridge or LiminalDB compatibility pin mismatch"));
    }
    if bundle.transition_id != "gse184241-geneformer-v1-inference-v0-1"
        || bundle.subject_id != "GSE184241"
        || bundle.action != "GENEFORMER_V1_INFERENCE"
    {
        return Err(anyhow!("unexpected governed inference transition"));
    }
    if bundle.supersession.relation != "SUPERSEDES"
        || bundle.supersession.predecessor_transition_id.as_deref() != Some(EXPECTED_PREDECESSOR_TRANSITION)
        || bundle.supersession.predecessor_authorization_ref.as_deref() != Some(EXPECTED_PREDECESSOR_AUTHORIZATION)
    {
        return Err(anyhow!("exact predecessor ancestry mismatch"));
    }
    if !bundle.storage_boundary.temporary_ledger_only
        || bundle.storage_boundary.production_write
        || bundle.storage_boundary.external_submission
        || bundle.storage_boundary.deployment
        || bundle.storage_boundary.merge
    {
        return Err(anyhow!("storage or authority boundary violation"));
    }
    if bundle.records.len() != 7 {
        return Err(anyhow!("expected exactly seven transition records"));
    }
    if bundle.records[0].kind != "authorization" {
        return Err(anyhow!("first record must be the authorization record"));
    }
    let current_authorization = bundle.records[0].record_ref.clone();
    if current_authorization == EXPECTED_PREDECESSOR_AUTHORIZATION {
        return Err(anyhow!("current authorization equals predecessor authorization"));
    }
    for (index, record) in bundle.records.iter().enumerate().skip(1) {
        if record.links.authorization_ref.as_deref() != Some(current_authorization.as_str()) {
            return Err(anyhow!("record {index} does not reference current authorization"));
        }
        if record.links.authorization_ref.as_deref() == Some(EXPECTED_PREDECESSOR_AUTHORIZATION) {
            return Err(anyhow!("record {index} imports predecessor authority"));
        }
    }
    if ledger_root.exists() {
        fs::remove_dir_all(&ledger_root).context("remove stale temporary ledger")?;
    }
    fs::create_dir_all(&ledger_root).context("create temporary ledger root")?;
    let mut ledger = TrustworthyTransitionLedger::open(&ledger_root).context("open temporary ledger")?;
    for record in bundle.records {
        if record.side_effect_committed {
            return Err(anyhow!("side effects are forbidden in this transition"));
        }
        ledger.append(TransitionEventInput {
            transition_id: bundle.transition_id.clone(),
            subject_id: bundle.subject_id.clone(),
            kind: record_kind(&record.kind)?,
            record_ref: record.record_ref,
            payload_digest: record.payload_digest,
            links: TransitionLinks {
                authorization_ref: record.links.authorization_ref,
                observation_refs: record.links.observation_refs,
                response_integrity_ref: record.links.response_integrity_ref,
                causal_audit_ref: record.links.causal_audit_ref,
                previous_continuity_ref: record.links.previous_continuity_ref,
            },
            dimensions: convert_dimensions(record.dimensions)?,
            side_effect_committed: Some(false),
            captured_at_ms: record.captured_at_ms,
        }).with_context(|| format!("append {}", record.kind))?;
    }
    let projection_before = ledger.projection(&bundle.transition_id).cloned().context("projection missing before snapshot")?;
    let event_count_before = ledger.event_count();
    let snapshot = ledger.write_snapshot(projection_before.last_sequence.saturating_add(1)).context("write snapshot")?;
    drop(ledger);
    let reopened = TrustworthyTransitionLedger::open(&ledger_root).context("reopen and replay ledger")?;
    let projection_after = reopened.projection(&bundle.transition_id).cloned().context("projection missing after reopen")?;
    let projection_equal = projection_before == projection_after;
    if !projection_equal {
        return Err(anyhow!("projection changed after snapshot plus full replay"));
    }
    if projection_after.side_effect_committed {
        return Err(anyhow!("replayed projection committed a forbidden side effect"));
    }
    let posture = projection_after.dimensions.as_ref().map(|dimensions| dimensions.continuity_posture.clone()).context("final continuity dimensions missing")?;
    let verdict = match posture {
        ContinuityPosture::ReportOnly => "RECOVERED_REPORT_ONLY",
        ContinuityPosture::Blocked => "RECOVERED_BLOCKED",
        other => return Err(anyhow!("unexpected final continuity posture: {other:?}")),
    };
    let receipt = Receipt {
        schema_version: "0.1.0",
        artifact_type: "liminaldb_geneformer_inference_replay_receipt",
        liminaldb_commit: EXPECTED_LIMINALDB_COMMIT,
        bundle_sha256: sha256_ref(&bundle_bytes),
        transition_id: projection_after.transition_id.clone(),
        subject_id: projection_after.subject_id.clone(),
        supersession_relation: bundle.supersession.relation,
        predecessor_transition_id: bundle.supersession.predecessor_transition_id,
        predecessor_authorization_ref: bundle.supersession.predecessor_authorization_ref,
        event_count_before_reopen: event_count_before,
        event_count_after_reopen: reopened.event_count(),
        snapshot_digest: snapshot.snapshot_digest().to_string(),
        snapshot_event_count: snapshot.event_count(),
        projection_count: snapshot.projection_count(),
        projection_equal_after_reopen: projection_equal,
        final_authorization_ref: projection_after.authorization_ref.clone(),
        final_observation_refs: projection_after.observation_refs.clone(),
        final_response_integrity_ref: projection_after.response_integrity_ref.clone(),
        final_causal_audit_ref: projection_after.causal_audit_ref.clone(),
        final_continuity_snapshot_ref: projection_after.continuity_snapshot_ref.clone(),
        final_dimensions: projection_after.dimensions.clone(),
        final_side_effect_committed: projection_after.side_effect_committed,
        final_event_count: projection_after.event_count,
        final_event_hash: projection_after.last_event_hash.clone(),
        verdict,
    };
    if let Some(parent) = receipt_path.parent() {
        fs::create_dir_all(parent).context("create receipt directory")?;
    }
    fs::write(&receipt_path, serde_json::to_vec_pretty(&receipt)?).context("write inference replay receipt")?;
    println!("{}", serde_json::to_string(&receipt)?);
    Ok(())
}
