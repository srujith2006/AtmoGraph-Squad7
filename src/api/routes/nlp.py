"""NLP Ingestion API Bridge receiving spaCy and HuggingFace NER disruption entities.

Provides webhook ingestion, automatic graph entity linking, live disruption propagation,
and historical alert query routes.
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query, status

from src.core.config import get_settings
from src.core.logging import get_logger
from src.core.exceptions import EntityNotFoundError, PayloadValidationError
from src.schemas.graph import (
    DisruptionSeverity,
    RiskLevel,
    NodeStatus,
    NLPDisruptionAlert,
)
from src.schemas.nlp import (
    NLPIngestRequest,
    NLPIngestResponse,
    MatchedNodeImpact,
)
import src.api.routes.graph as graph_state

logger = get_logger("atmograph.nlp")

router = APIRouter(prefix="/nlp", tags=["NLP Ingestion Engine"])

# In-memory storage for processed disruption alerts
_PROCESSED_ALERTS: Dict[str, NLPDisruptionAlert] = {}


def _resolve_entities_to_graph_nodes(
    request: NLPIngestRequest,
    target_severity: DisruptionSeverity,
) -> List[MatchedNodeImpact]:
    """Link extracted news entities to supply chain graph nodes and apply risk state changes."""
    matched_nodes: List[MatchedNodeImpact] = []
    seen_node_ids = set()

    # Search tokens from named entities, detected risks, and article body
    search_terms = set()
    for ent in request.entities:
        search_terms.add(ent.name.strip().lower())
    for risk in request.detected_risks:
        if risk.location:
            search_terms.add(risk.location.strip().lower())
        for affected in risk.affected_entities:
            search_terms.add(affected.strip().lower())

    # Map DisruptionSeverity to Node RiskLevel
    risk_mapping = {
        DisruptionSeverity.LOW: RiskLevel.LOW,
        DisruptionSeverity.MEDIUM: RiskLevel.MEDIUM,
        DisruptionSeverity.HIGH: RiskLevel.HIGH,
        DisruptionSeverity.CRITICAL: RiskLevel.CRITICAL,
    }
    new_risk = risk_mapping.get(target_severity, RiskLevel.HIGH)

    # Search against existing nodes in graph state
    for node_id, node in graph_state._MOCK_NODES.items():
        if node_id in seen_node_ids:
            continue

        node_name_lower = node.name.lower()
        country_lower = node.country.lower()
        location_lower = (node.location or "").lower()
        key_output_lower = (node.key_output or "").lower()

        matched_term = None
        for term in search_terms:
            if len(term) < 3:
                continue
            if (
                term in node_name_lower
                or term in country_lower
                or term in location_lower
                or term in key_output_lower
            ):
                matched_term = term
                break

        if matched_term:
            prev_risk = node.risk_level
            # Apply disruption to node state
            node.risk_level = new_risk
            node.status = NodeStatus.DISRUPTED if new_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL) else NodeStatus.DEGRADED
            node.metadata["last_nlp_incident"] = request.title
            node.metadata["nlp_matched_term"] = matched_term
            node.metadata["nlp_ingested_at"] = datetime.now(timezone.utc).isoformat()

            # Propagate delays to connected routes
            for edge in graph_state._MOCK_EDGES.values():
                if edge.from_id == node_id or edge.to_id == node_id:
                    edge.active_disruption = True
                    edge.lead_time_days += 10.0
                    edge.risk_multiplier = 3.0
                    edge.notes = f"Delayed by NLP detected event: {request.title}"

            seen_node_ids.add(node_id)
            matched_nodes.append(
                MatchedNodeImpact(
                    node_id=node.id,
                    node_name=node.name,
                    country=node.country,
                    matched_entity=matched_term,
                    previous_risk_level=prev_risk,
                    new_risk_level=new_risk,
                    disruption_applied=True,
                )
            )

    return matched_nodes


@router.post("/ingest", response_model=NLPIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_nlp_entities(
    payload: NLPIngestRequest,
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
) -> NLPIngestResponse:
    """Webhook endpoint receiving NLP entity extraction payloads from spaCy / HuggingFace pipelines.

    Resolves mentioned geopolitical entities and organizations onto graph nodes,
    updates risk states, and stores the processed alert.
    """
    settings = get_settings()

    # Optional webhook token authentication
    if x_webhook_secret is not None:
        if x_webhook_secret != settings.nlp_webhook_secret:
            logger.warning(
                "Unauthorized NLP ingestion webhook attempt: invalid secret header",
                extra={"provided_header": x_webhook_secret[:4] + "***"}
            )
            raise PayloadValidationError(
                message="Invalid webhook authentication secret header 'X-Webhook-Secret'.",
                details={"status": "unauthorized"}
            )

    if not payload.article or not payload.article.strip():
        raise PayloadValidationError(
            message="Article text cannot be empty.",
            details={"field": "article"}
        )

    # Determine dominant severity from detected risks
    severities = [r.severity for r in payload.detected_risks if r.severity]
    if DisruptionSeverity.CRITICAL in severities:
        applied_severity = DisruptionSeverity.CRITICAL
    elif DisruptionSeverity.HIGH in severities:
        applied_severity = DisruptionSeverity.HIGH
    elif DisruptionSeverity.MEDIUM in severities:
        applied_severity = DisruptionSeverity.MEDIUM
    else:
        applied_severity = DisruptionSeverity.LOW

    # 1. Resolve entities and update graph topology
    matched_impacts = _resolve_entities_to_graph_nodes(payload, applied_severity)
    impacted_node_ids = [m.node_id for m in matched_impacts]

    # 2. Construct Disruption Alert Record
    alert_id = f"alert-{uuid.uuid4().hex[:12]}"
    headline = payload.title or (payload.article.splitlines()[0] if payload.article else "Supply Chain Disruption Alert")
    primary_risk_name = payload.detected_risks[0].risk if payload.detected_risks else "Supply Chain Disruption"
    location_name = payload.detected_risks[0].location if payload.detected_risks else None

    alert_record = NLPDisruptionAlert(
        alert_id=alert_id,
        title=headline,
        source=payload.source or "spaCy / HuggingFace Ingestion",
        published_at=datetime.now(timezone.utc),
        severity=applied_severity,
        primary_risk=primary_risk_name,
        location=location_name,
        affected_node_ids=impacted_node_ids,
        entities=payload.entities,
        evidence_text=payload.article[:300],
        confidence_score=payload.confidence_score,
    )

    _PROCESSED_ALERTS[alert_id] = alert_record

    logger.info(
        f"NLP disruption alert processed: {alert_id} - matched {len(matched_impacts)} nodes",
        extra={
            "alert_id": alert_id,
            "severity": applied_severity,
            "matched_nodes_count": len(matched_impacts),
            "matched_node_ids": impacted_node_ids,
        }
    )

    return NLPIngestResponse(
        status="ingested",
        alert_id=alert_id,
        title=headline,
        severity=applied_severity,
        entities_count=len(payload.entities),
        matched_nodes_count=len(matched_impacts),
        matched_nodes=matched_impacts,
        ingested_at=datetime.now(timezone.utc),
    )


@router.get("/alerts", response_model=List[NLPDisruptionAlert], status_code=status.HTTP_200_OK)
async def list_disruption_alerts(
    severity: Optional[DisruptionSeverity] = Query(None, description="Filter by disruption severity rating"),
    node_id: Optional[str] = Query(None, description="Filter alerts affecting a specific node ID"),
) -> List[NLPDisruptionAlert]:
    """Retrieve history of processed NLP disruption alerts."""
    alerts = list(_PROCESSED_ALERTS.values())
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    if node_id:
        alerts = [a for a in alerts if node_id in a.affected_node_ids]
    return sorted(alerts, key=lambda a: a.published_at, reverse=True)


@router.get("/alerts/{alert_id}", response_model=NLPDisruptionAlert, status_code=status.HTTP_200_OK)
async def get_disruption_alert_by_id(alert_id: str) -> NLPDisruptionAlert:
    """Retrieve detailed NLP disruption alert by its unique alert ID."""
    if alert_id not in _PROCESSED_ALERTS:
        raise EntityNotFoundError(entity_type="DisruptionAlert", entity_id=alert_id)
    return _PROCESSED_ALERTS[alert_id]


@router.delete("/alerts", status_code=status.HTTP_200_OK)
async def clear_alerts_for_testing():
    """Clear in-memory alert history for testing purposes."""
    _PROCESSED_ALERTS.clear()
    return {"status": "cleared", "total_alerts": 0}
