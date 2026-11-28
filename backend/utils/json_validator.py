
import json
import sys
from pathlib import Path


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[1]

DEFAULT_JSON_FILE = (
    BACKEND_DIR / "data" / "articles" / "team_output.json"
)


# --------------------------------------------------
# SUPPORTED VALUES
# --------------------------------------------------

SUPPORTED_ENTITY_TYPES = {
    "REGION",
    "LOCATION",
    "PORT"
}

SUPPORTED_RELATIONSHIP_TYPES = {
    "EXPERIENCING",
    "CAUSES",
    "LOCATED_IN",
    "AFFECTED_BY"
}

SUPPORTED_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH"
}

SUPPORTED_REVIEW_STATUSES = {
    "CANDIDATE",
    "NEEDS_REVIEW",
    "CONTRADICTED"
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def is_string(value):
    return isinstance(value, str) and bool(value.strip())


def validate_string_field(data, field, errors, required=True):
    value = data.get(field)

    if required and not is_string(value):
        errors.append(f"'{field}' must be a non-empty string.")

    elif not required and value is not None and not isinstance(value, str):
        errors.append(f"'{field}' must be a string or null.")


def validate_severity(value, field, errors):
    if value not in SUPPORTED_SEVERITIES:
        errors.append(
            f"'{field}' must be one of "
            f"{sorted(SUPPORTED_SEVERITIES)}."
        )


# --------------------------------------------------
# ENTITY VALIDATION
# --------------------------------------------------

def validate_entities(entities, errors):

    if not isinstance(entities, list):
        errors.append("'entities' must be a list.")
        return

    for index, entity in enumerate(entities):

        if not isinstance(entity, dict):
            errors.append(f"Entity {index} must be an object.")
            continue

        validate_string_field(
            entity, "name", errors
        )

        entity_type = entity.get("type")

        if entity_type not in SUPPORTED_ENTITY_TYPES:
            errors.append(
                f"Entity {index}: unsupported type '{entity_type}'."
            )


# --------------------------------------------------
# RELATIONSHIP VALIDATION
# --------------------------------------------------

def validate_relationships(relationships, errors):

    if not isinstance(relationships, list):
        errors.append("'relationships' must be a list.")
        return

    for index, relationship in enumerate(relationships):

        if not isinstance(relationship, dict):
            errors.append(
                f"Relationship {index} must be an object."
            )
            continue

        for field in ("source", "target", "relationship"):
            validate_string_field(
                relationship, field, errors
            )

        relationship_type = relationship.get("relationship")

        if relationship_type not in SUPPORTED_RELATIONSHIP_TYPES:
            errors.append(
                f"Relationship {index}: unsupported relationship "
                f"type '{relationship_type}'."
            )

        validate_string_field(
            relationship, "evidence", errors, required=False
        )


# --------------------------------------------------
# DETECTED RISK VALIDATION
# --------------------------------------------------

def validate_detected_risks(detected_risks, errors):

    if not isinstance(detected_risks, list):
        errors.append("'detected_risks' must be a list.")
        return

    for index, risk in enumerate(detected_risks):

        if not isinstance(risk, dict):
            errors.append(
                f"Detected risk {index} must be an object."
            )
            continue

        validate_string_field(risk, "risk", errors)

        validate_string_field(
            risk, "location", errors, required=False
        )

        validate_string_field(
            risk, "evidence", errors, required=False
        )

        validate_severity(
            risk.get("severity"),
            f"detected_risks[{index}].severity",
            errors
        )


# --------------------------------------------------
# RISK REVIEW CANDIDATE VALIDATION
# --------------------------------------------------

def validate_risk_review_candidates(candidates, errors):

    if not isinstance(candidates, list):
        errors.append("'risk_review_candidates' must be a list.")
        return

    for index, candidate in enumerate(candidates):

        if not isinstance(candidate, dict):
            errors.append(
                f"Risk review candidate {index} must be an object."
            )
            continue

        validate_string_field(candidate, "risk", errors)

        validate_string_field(
            candidate, "location", errors, required=False
        )

        source_locations = candidate.get("source_locations")

        if not isinstance(source_locations, list):
            errors.append(
                f"Candidate {index}: 'source_locations' must be a list."
            )
        elif not all(isinstance(item, str) for item in source_locations):
            errors.append(
                f"Candidate {index}: every source location must be a string."
            )

        validate_string_field(
            candidate, "evidence", errors, required=False
        )

        validate_severity(
            candidate.get("severity"),
            f"risk_review_candidates[{index}].severity",
            errors
        )

        status = candidate.get("status")

        if status not in SUPPORTED_REVIEW_STATUSES:
            errors.append(
                f"Candidate {index}: unsupported status '{status}'."
            )


# --------------------------------------------------
# METADATA VALIDATION
# --------------------------------------------------

def validate_metadata(metadata, errors):

    if not isinstance(metadata, dict):
        errors.append("'metadata' must be an object.")
        return

    required_fields = [
        "date",
        "region",
        "latitude",
        "longitude",
        "maritime_label",
        "found_ports",
        "contains_port_info",
        "if_labeled",
        "year",
        "month",
        "week",
        "category",
        "summarized_label",
        "gpt_4o_label",
        "source_severity"
    ]

    for field in required_fields:
        if field not in metadata:
            errors.append(
                f"Metadata is missing required field '{field}'."
            )

    for field in (
        "date",
        "region",
        "category",
        "summarized_label",
        "source_severity"
    ):
        if field in metadata and not is_string(metadata[field]):
            errors.append(
                f"Metadata '{field}' must be a non-empty string."
            )

    for field in ("latitude", "longitude"):
        value = metadata.get(field)

        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            errors.append(
                f"Metadata '{field}' must be a number or null."
            )

    for field in (
        "maritime_label",
        "contains_port_info"
    ):
        if field in metadata and not isinstance(metadata[field], bool):
            errors.append(
                f"Metadata '{field}' must be a boolean."
            )

    if (
        "if_labeled" in metadata
        and metadata["if_labeled"] is not None
        and not isinstance(metadata["if_labeled"], bool)
    ):
        errors.append(
            "Metadata 'if_labeled' must be a boolean or null."
        )

    for field in ("year", "month", "week"):
        value = metadata.get(field)

        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int)
        ):
            errors.append(
                f"Metadata '{field}' must be an integer or null."
            )

    found_ports = metadata.get("found_ports")

    if not isinstance(found_ports, list):
        errors.append("'metadata.found_ports' must be a list.")

    elif not all(isinstance(port, str) for port in found_ports):
        errors.append(
            "Every item in 'metadata.found_ports' must be a string."
        )

    gpt_label = metadata.get("gpt_4o_label")

    if not isinstance(gpt_label, dict):
        errors.append("'metadata.gpt_4o_label' must be an object.")


# --------------------------------------------------
# SINGLE ARTICLE VALIDATION
# --------------------------------------------------

def validate_article(article):

    errors = []

    if not isinstance(article, dict):
        return ["Article must be a JSON object."]

    required_fields = [
        "record_id",
        "source",
        "article",
        "metadata",
        "raw_fields",
        "entities",
        "relationships",
        "detected_risks",
        "severity_note",
        "risk_review_candidates_previous",
        "detected_risks_initial",
        "risk_review_candidates"
    ]

    for field in required_fields:
        if field not in article:
            errors.append(
                f"Article is missing required field '{field}'."
            )

    # Record ID
    record_id = article.get("record_id")

    if isinstance(record_id, bool) or not isinstance(record_id, int):
        errors.append("'record_id' must be an integer.")

    # Main text fields
    validate_string_field(article, "source", errors)
    validate_string_field(article, "article", errors)

    validate_string_field(
        article, "severity_note", errors, required=False
    )

    # Metadata
    if "metadata" in article:
        validate_metadata(article["metadata"], errors)

    # Raw source fields
    if not isinstance(article.get("raw_fields"), dict):
        errors.append("'raw_fields' must be an object.")

    # Extracted entities and relationships
    if "entities" in article:
        validate_entities(article["entities"], errors)

    if "relationships" in article:
        validate_relationships(article["relationships"], errors)

    # Confirmed/detected risks
    if "detected_risks" in article:
        validate_detected_risks(
            article["detected_risks"], errors
        )

    # Previous candidate data is preserved and checked as a list.
    for field in (
        "risk_review_candidates_previous",
        "detected_risks_initial"
    ):
        if field in article and not isinstance(article[field], list):
            errors.append(f"'{field}' must be a list.")

    # Current risk review candidates
    if "risk_review_candidates" in article:
        validate_risk_review_candidates(
            article["risk_review_candidates"], errors
        )

    return errors


# --------------------------------------------------
# SINGLE OR BATCH DATASET VALIDATION
# --------------------------------------------------

def validate_dataset(data):

    if isinstance(data, dict):
        records = [data]

    elif isinstance(data, list):
        records = data

    else:
        return [], ["JSON input must be an object or a list of objects."]

    valid_records = []
    all_errors = []

    seen_record_ids = set()

    for index, record in enumerate(records):

        errors = validate_article(record)

        if isinstance(record, dict):
            record_id = record.get("record_id")

            if isinstance(record_id, int) and not isinstance(record_id, bool):
                if record_id in seen_record_ids:
                    errors.append(
                        f"Duplicate record_id: {record_id}."
                    )
                else:
                    seen_record_ids.add(record_id)

        if errors:
            for error in errors:
                all_errors.append(
                    f"Record at index {index}: {error}"
                )
        else:
            valid_records.append(record)

    return valid_records, all_errors


# --------------------------------------------------
# JSON FILE VALIDATION
# --------------------------------------------------

def validate_json_file(file_path=DEFAULT_JSON_FILE):

    file_path = Path(file_path)

    if not file_path.exists():
        print(f"ERROR: JSON file not found: {file_path}")
        return False

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        print("ERROR: Invalid JSON format.")
        print(error)
        return False

    valid_records, errors = validate_dataset(data)

    total_records = len(data) if isinstance(data, list) else 1

    print("\n========== JSON VALIDATION REPORT ==========")
    print(f"File: {file_path.name}")
    print(f"Total records: {total_records}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Invalid records: {total_records - len(valid_records)}")

    if errors:
        print("\nValidation errors:")

        for error in errors[:50]:
            print(f"- {error}")

        if len(errors) > 50:
            print(f"... and {len(errors) - 50} more errors.")

        print("\nVALIDATION FAILED.")
        return False

    print("\nVALIDATION SUCCESSFUL.")
    return True


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    json_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_JSON_FILE
    )

    validate_json_file(json_file)
