"""Pydantic schemas for NLP news ingestion webhook, entity extraction, and disruption alerts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.graph import DisruptionSeverity, NLPExtractedEntity, NLPDisruptionAlert


class NLPRelationship(BaseModel):
    """Semantic relation between two extracted entities in breaking news text."""
    entity_1: str = Field(description="First entity mention")
    entity_2: str = Field(description="Second entity mention")
    relation: str = Field(description="Relation predicate: e.g. LOCATED_IN, CAUSES, AFFECTED_BY, EXPERIENCING")
    evidence: Optional[str] = Field(default=None, description="Supporting sentence excerpt")


class NLPDetectedRisk(BaseModel):
    """Domain risk event classified by NLP model."""
    risk: str = Field(description="Risk taxonomy description, e.g. 'Port congestion', 'Factory strike'")
    location: Optional[str] = Field(default=None, description="Geographic location of event")
    affected_entities: List[str] = Field(default_factory=list, description="Target companies, facilities, or commodities")
    severity: DisruptionSeverity = Field(default=DisruptionSeverity.MEDIUM, description="Assessed severity level")
    evidence: Optional[str] = Field(default=None, description="Sentence text proving the risk")

    model_config = ConfigDict(use_enum_values=True)


class NLPIngestRequest(BaseModel):
    """Payload sent by spaCy / HuggingFace worker to the ingestion webhook."""
    article: str = Field(description="Raw news article text or breaking report excerpt")
    title: Optional[str] = Field(default="Live Breaking News Disruption", description="Article headline")
    source: Optional[str] = Field(default="spaCy/HuggingFace NER Pipeline", description="News origin or crawler ID")
    entities: List[NLPExtractedEntity] = Field(default_factory=list, description="Named entities identified in text")
    relationships: List[NLPRelationship] = Field(default_factory=list, description="Extracted entity relationships")
    detected_risks: List[NLPDetectedRisk] = Field(default_factory=list, description="Categorized supply chain risks")
    severity_note: Optional[str] = Field(default=None, description="Model explanation for severity classification")
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0, description="Overall NLP confidence (0-1)")

    model_config = ConfigDict(use_enum_values=True)


class MatchedNodeImpact(BaseModel):
    """Graph node linked to an extracted entity from the news text."""
    node_id: str
    node_name: str
    country: str
    matched_entity: str
    previous_risk_level: str
    new_risk_level: str
    disruption_applied: bool


class NLPIngestResponse(BaseModel):
    """Response returned by webhook upon successful ingestion and entity linking."""
    status: str = Field(default="ingested", description="Processing status")
    alert_id: str = Field(description="Created disruption alert UUID")
    title: str = Field(description="Alert headline")
    severity: str = Field(description="Applied severity level")
    entities_count: int = Field(description="Total named entities received")
    matched_nodes_count: int = Field(description="Count of supply chain graph nodes impacted")
    matched_nodes: List[MatchedNodeImpact] = Field(default_factory=list, description="Linked graph nodes details")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
