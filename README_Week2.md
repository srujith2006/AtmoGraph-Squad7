# 🌐 AtmoGraph
### Supply Chain Ripple Effect Predictor

**WEEK 02 | DATA STRUCTURING & RELATIONSHIP EXTRACTION**

## 1. Project Overview

AtmoGraph aims to identify supply chain disruptions, understand their impact, and represent connections between companies, locations, shipments, and potential risks using structured data.

## 2. Week 2 Development Focus

This week's work focused on transforming basic article-based JSON data into a more meaningful and structured format for backend integration.

## 3. Key Technical Contributions

**A. Entity Identification**
- Identified important entities from the given news article.
- Organized geographical locations and organizations.
- Added structured entity information.

**B. Relationship Extraction**

Introduced meaningful relationship types:

- `LOCATED_IN`
- `AFFECTED_BY`
- `CAUSES`
- `EXPERIENCING`

These relationships help represent connections between supply chain entities and disruptions.

**C. Risk-to-Entity Mapping**
- Connected detected risks with relevant entities.
- Identified affected shipments and organizations.
- Added location information wherever supported by the article.

**D. Risk Assessment**
- Introduced LOW, MEDIUM and HIGH severity categories.
- Added supporting article evidence for detected risks.
- Used MEDIUM as an estimated classification where appropriate.

## 4. Sample Article Analysis

**Article:** Port Congestion in Singapore

The sample article describes:
- Port congestion in Singapore.
- Delayed semiconductor shipments.
- Supply chain disruptions affecting Samsung and Intel.

This information was structured into entities, relationships and detected risks.

## 5. Technology & Tools

- Python
- JSON
- Google Colab
- GitHub

## 6. Backend Integration Objective

The updated JSON structure is intended to support the backend team in converting extracted information into Neo4j graph database nodes and relationships.

## 7. Week 2 Outcome

The initial JSON structure was improved with meaningful relationship extraction, entity-based risk mapping and evidence-supported risk information.

**Current Status:** Week 2 data structuring and JSON enhancement completed.

---

*AtmoGraph | Technical Development Documentation | Week 2*
