"""Mock breaking news and spaCy / HuggingFace NER disruption fixtures.

Simulates live news articles, extracted entity metadata, semantic relationships,
and risk severity ratings for supply chain disruption testing.
"""

from typing import Any, Dict


# ==============================================================================
# Fixture 1: European Port Strike (Directly matches project problem statement)
# "Predicting multi-hop global supply chain delays (e.g. European port strike
# delaying North American electronics by 3 months)"
# ==============================================================================

EUROPEAN_PORT_STRIKE_FIXTURE: Dict[str, Any] = {
    "title": "Major Dockworkers Strike Halts Rotterdam Gateway Terminals",
    "source": "Reuters Maritime Wire",
    "article": (
        "A 72-hour general dockworkers strike has paralyzed container berths at Rotterdam Gateway Logistics. "
        "Container vessels cannot dock or discharge cargo. Freight forwarders warn that transatlantic electronics "
        "shipments to North America Retail Electronics will suffer delays of up to 3 months as backlogs mount."
    ),
    "entities": [
        {"id": "E1", "name": "Rotterdam", "type": "GPE", "confidence": 0.99},
        {"id": "E2", "name": "Dockworkers Strike", "type": "RISK", "confidence": 0.97},
        {"id": "E3", "name": "Rotterdam Gateway Logistics", "type": "ORG", "confidence": 0.96},
        {"id": "E4", "name": "North America Retail Electronics", "type": "ORG", "confidence": 0.94},
        {"id": "E5", "name": "Transatlantic electronics shipments", "type": "SHIPMENT", "confidence": 0.91},
    ],
    "relationships": [
        {
            "entity_1": "Dockworkers Strike",
            "entity_2": "Rotterdam Gateway Logistics",
            "relation": "LOCATED_IN",
            "evidence": "A 72-hour general dockworkers strike has paralyzed container berths at Rotterdam Gateway Logistics."
        },
        {
            "entity_1": "Dockworkers Strike",
            "entity_2": "Transatlantic electronics shipments",
            "relation": "CAUSES",
            "evidence": "Transatlantic electronics shipments to North America Retail Electronics will suffer delays."
        },
        {
            "entity_1": "North America Retail Electronics",
            "entity_2": "Transatlantic electronics shipments",
            "relation": "AFFECTED_BY",
            "evidence": "North America Retail Electronics will suffer delays of up to 3 months."
        }
    ],
    "detected_risks": [
        {
            "risk": "Port Strike & Terminal Shutdown",
            "location": "Rotterdam",
            "affected_entities": ["Rotterdam Gateway Logistics", "North America Retail Electronics"],
            "severity": "CRITICAL",
            "evidence": "A 72-hour general dockworkers strike has paralyzed container berths."
        }
    ],
    "severity_note": "CRITICAL rating due to primary European transshipment hub total closure.",
    "confidence_score": 0.96,
}


# ==============================================================================
# Fixture 2: Singapore Port Congestion (Matches teammate's sample_article.json)
# ==============================================================================

SINGAPORE_PORT_CONGESTION_FIXTURE: Dict[str, Any] = {
    "title": "Port Congestion in Singapore Delays Semiconductor Shipments",
    "source": "Singapore Maritime Daily",
    "article": (
        "Port congestion in Singapore has delayed semiconductor shipments. "
        "Samsung and Intel are facing supply chain disruptions."
    ),
    "entities": [
        {"id": "E1", "name": "Singapore", "type": "GPE", "confidence": 0.98},
        {"id": "E2", "name": "Port congestion", "type": "RISK", "confidence": 0.95},
        {"id": "E3", "name": "Semiconductor shipments", "type": "SHIPMENT", "confidence": 0.93},
        {"id": "E4", "name": "Shipment delay", "type": "RISK", "confidence": 0.92},
        {"id": "E5", "name": "Samsung", "type": "ORG", "confidence": 0.95},
        {"id": "E6", "name": "Intel", "type": "ORG", "confidence": 0.94},
        {"id": "E7", "name": "Supply chain disruption", "type": "RISK", "confidence": 0.90},
    ],
    "relationships": [
        {
            "entity_1": "Port congestion",
            "entity_2": "Singapore",
            "relation": "LOCATED_IN",
            "evidence": "Port congestion in Singapore has delayed semiconductor shipments."
        },
        {
            "entity_1": "Port congestion",
            "entity_2": "Shipment delay",
            "relation": "CAUSES",
            "evidence": "Port congestion in Singapore has delayed semiconductor shipments."
        },
        {
            "entity_1": "Semiconductor shipments",
            "entity_2": "Port congestion",
            "relation": "AFFECTED_BY",
            "evidence": "Port congestion in Singapore has delayed semiconductor shipments."
        }
    ],
    "detected_risks": [
        {
            "risk": "Port congestion",
            "location": "Singapore",
            "affected_entities": ["Semiconductor shipments"],
            "severity": "MEDIUM",
            "evidence": "Port congestion in Singapore has delayed semiconductor shipments."
        }
    ],
    "severity_note": "MEDIUM estimated classification based on reported delays in transshipment queue.",
    "confidence_score": 0.91,
}


# ==============================================================================
# Fixture 3: Shenzhen Silicon Wafer Fab Disruption
# ==============================================================================

SHENZHEN_FAB_DISRUPTION_FIXTURE: Dict[str, Any] = {
    "title": "Power Interruption Halts Production at Shenzhen Micro-Wafer Corp",
    "source": "Asia Tech Supply Bulletin",
    "article": (
        "A localized electrical grid failure and subsequent chemical contamination have halted cleanroom "
        "operations at Shenzhen Micro-Wafer Corp. Ingot slicing and raw IC substrate manufacturing are suspended, "
        "triggering urgent component shortages for downstream assembly partners in Taiwan and Germany."
    ),
    "entities": [
        {"id": "E1", "name": "Shenzhen", "type": "GPE", "confidence": 0.99},
        {"id": "E2", "name": "Shenzhen Micro-Wafer Corp", "type": "ORG", "confidence": 0.98},
        {"id": "E3", "name": "Power failure", "type": "RISK", "confidence": 0.94},
        {"id": "E4", "name": "Chemical contamination", "type": "RISK", "confidence": 0.93},
        {"id": "E5", "name": "Silicon wafer substrates", "type": "SHIPMENT", "confidence": 0.92},
    ],
    "relationships": [
        {
            "entity_1": "Power failure",
            "entity_2": "Shenzhen Micro-Wafer Corp",
            "relation": "LOCATED_IN",
            "evidence": "Electrical grid failure has halted cleanroom operations at Shenzhen Micro-Wafer Corp."
        }
    ],
    "detected_risks": [
        {
            "risk": "Wafer Fab Cleanroom Contamination",
            "location": "Shenzhen",
            "affected_entities": ["Shenzhen Micro-Wafer Corp"],
            "severity": "HIGH",
            "evidence": "Chemical contamination halted cleanroom operations at Shenzhen Micro-Wafer Corp."
        }
    ],
    "severity_note": "HIGH severity due to 3-week semiconductor wafer production stoppage.",
    "confidence_score": 0.95,
}
