
import json
import sys
from pathlib import Path

# Locate backend directory
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Default GMRID JSON input file
DEFAULT_JSON_FILE = (
    BACKEND_DIR / "data" / "articles" / "sample_article.json"
)

# Supported entity types
SUPPORTED_ENTITY_TYPES = {
    "GPE",
    "RISK",
    "SHIPMENT",
    "ORG"
}

# Supported relationship types
SUPPORTED_RELATIONSHIPS = {
    "LOCATED_IN",
    "CAUSES",
    "OCCURS_IN",
    "AFFECTS",
    "AFFECTED_BY",
    "EXPERIENCING"
}

# Allowed NLP risk severity levels
SUPPORTED_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH"
}


def print_errors(errors):
    """Display validation errors."""

    print("\nJSON validation failed!")

    for error in errors:
        print(f"- {error}")

    return False


def is_number_or_none(value):
    """Check whether a value is numeric or None."""

    return (
        value is None
        or (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )
    )


def validate_metadata(metadata, errors):
    """Validate GMRID metadata."""

    if not isinstance(metadata, dict):
        errors.append("metadata must be an object!")
        return

    # String fields that may be null
    string_fields = [
        "date",
        "region",
        "maritime_label",
        "if_labeled",
        "summarized_label",
        "source_severity"
    ]

    for field in string_fields:
        if field in metadata:
            value = metadata[field]

            if value is not None and not isinstance(value, str):
                errors.append(
                    f"metadata.{field} must be a string or null!"
                )

    # Coordinates
    for field in ["latitude", "longitude"]:
        if field in metadata:
            if not is_number_or_none(metadata[field]):
                errors.append(
                    f"metadata.{field} must be a number or null!"
                )

    # Integer date fields
    for field in ["year", "month", "week"]:
        if field in metadata:
            value = metadata[field]

            if value is not None and (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                errors.append(
                    f"metadata.{field} must be an integer or null!"
                )

    # Port information
    if "found_ports" in metadata:
        found_ports = metadata["found_ports"]

        if not isinstance(found_ports, list):
            errors.append("metadata.found_ports must be a list!")
        else:
            for port in found_ports:
                if not isinstance(port, str) or not port.strip():
                    errors.append(
                        "Every metadata.found_ports item "
                        "must be a non-empty string!"
                    )

    if "contains_port_info" in metadata:
        if not isinstance(metadata["contains_port_info"], bool):
            errors.append(
                "metadata.contains_port_info must be a boolean!"
            )

    # Category information
    if "category" in metadata:
        categories = metadata["category"]

        if not isinstance(categories, list):
            errors.append("metadata.category must be a list!")
        else:
            for category in categories:
                if not isinstance(category, str) or not category.strip():
                    errors.append(
                        "Every metadata.category item "
                        "must be a non-empty string!"
                    )

    # GPT-4o classification
    if "gpt_4o_label" in metadata:
        label = metadata["gpt_4o_label"]

        if label is not None:
            if not isinstance(label, dict):
                errors.append(
                    "metadata.gpt_4o_label must be an object or null!"
                )
            else:
                category = label.get("category")
                tags = label.get("specific_tags")

                if category is not None and not isinstance(category, str):
                    errors.append(
                        "gpt_4o_label.category must be a string or null!"
                    )

                if tags is not None:
                    if not isinstance(tags, list):
                        errors.append(
                            "gpt_4o_label.specific_tags must be a list!"
                        )
                    else:
                        for tag in tags:
                            if not isinstance(tag, str) or not tag.strip():
                                errors.append(
                                    "Every specific_tags item "
                                    "must be a non-empty string!"
                                )


def validate_entities(entities, errors):
    """Validate NLP entities."""

    entity_names = set()
    entity_ids = set()
    entity_types = {}

    for index, entity in enumerate(entities):

        if not isinstance(entity, dict):
            errors.append(f"Entity {index + 1} must be an object!")
            continue

        name = entity.get("name")
        entity_type = entity.get("type")
        entity_id = entity.get("id")

        if not isinstance(name, str) or not name.strip():
            errors.append(
                f"Entity {index + 1}: invalid or missing name!"
            )
            continue

        if not isinstance(entity_type, str):
            errors.append(
                f"Entity {name}: missing or invalid type!"
            )
            continue

        if entity_type not in SUPPORTED_ENTITY_TYPES:
            errors.append(
                f"Entity {name}: unsupported type '{entity_type}'!"
            )
            continue

        if entity_id is not None:
            if not isinstance(entity_id, str) or not entity_id.strip():
                errors.append(
                    f"Entity {name}: ID must be a non-empty string!"
                )
            elif entity_id in entity_ids:
                errors.append(f"Duplicate entity ID: {entity_id}")
            else:
                entity_ids.add(entity_id)

        normalized_name = name.strip()

        if normalized_name in entity_names:
            errors.append(
                f"Duplicate entity name: {normalized_name}"
            )
        else:
            entity_names.add(normalized_name)
            entity_types[normalized_name] = entity_type

    return entity_names, entity_types


def validate_relationships(relationships, entity_names, errors):
    """Validate NLP relationships."""

    for index, relationship in enumerate(relationships):

        if not isinstance(relationship, dict):
            errors.append(
                f"Relationship {index + 1} must be an object!"
            )
            continue

        name_1 = relationship.get("entity_1")
        name_2 = relationship.get("entity_2")
        relation = relationship.get("relation")

        if not isinstance(name_1, str) or not name_1.strip():
            errors.append(
                f"Relationship {index + 1}: invalid entity_1!"
            )
            continue

        if not isinstance(name_2, str) or not name_2.strip():
            errors.append(
                f"Relationship {index + 1}: invalid entity_2!"
            )
            continue

        if not isinstance(relation, str):
            errors.append(
                f"Relationship {index + 1}: invalid relation!"
            )
            continue

        if name_1.strip() not in entity_names:
            errors.append(
                f"Unknown relationship source entity: {name_1}"
            )

        if name_2.strip() not in entity_names:
            errors.append(
                f"Unknown relationship target entity: {name_2}"
            )

        if relation not in SUPPORTED_RELATIONSHIPS:
            errors.append(
                f"Unsupported relationship type: {relation}"
            )

        evidence = relationship.get("evidence")

        if evidence is not None and not isinstance(evidence, str):
            errors.append(
                f"Relationship evidence must be a string: "
                f"{name_1} -> {name_2}"
            )


def validate_detected_risks(detected_risks, entity_types, entity_names, errors):
    """Validate detected risks."""

    for index, risk in enumerate(detected_risks):

        if not isinstance(risk, dict):
            errors.append(
                f"Detected risk {index + 1} must be an object!"
            )
            continue

        risk_name = risk.get("risk")
        severity = risk.get("severity")
        location = risk.get("location")
        affected_entities = risk.get("affected_entities")

        if not isinstance(risk_name, str) or not risk_name.strip():
            errors.append(
                f"Detected risk {index + 1}: invalid risk name!"
            )
            continue

        risk_name = risk_name.strip()

        if entity_types.get(risk_name) != "RISK":
            errors.append(
                f"'{risk_name}' is not a known RISK entity!"
            )

        if not isinstance(severity, str):
            errors.append(
                f"Risk {risk_name}: severity must be a string!"
            )
        elif severity not in SUPPORTED_SEVERITIES:
            errors.append(
                f"Risk {risk_name}: invalid severity '{severity}'!"
            )

        if location is not None:
            if not isinstance(location, str):
                errors.append(
                    f"Risk {risk_name}: location must be a string!"
                )
            elif location.strip() and entity_types.get(
                location.strip()
            ) != "GPE":
                errors.append(
                    f"Risk {risk_name}: unknown location '{location}'!"
                )

        if not isinstance(affected_entities, list):
            errors.append(
                f"Risk {risk_name}: affected_entities must be a list!"
            )
        else:
            for affected_name in affected_entities:
                if (
                    not isinstance(affected_name, str)
                    or affected_name.strip() not in entity_names
                ):
                    errors.append(
                        f"Risk {risk_name}: unknown affected entity "
                        f"'{affected_name}'!"
                    )

        evidence = risk.get("evidence")

        if evidence is not None and not isinstance(evidence, str):
            errors.append(
                f"Risk {risk_name}: evidence must be a string!"
            )


def validate_json(file_path):
    """Validate GMRID article JSON before Neo4j ingestion."""

    file_path = Path(file_path)
    errors = []

    if not file_path.exists():
        print(f"Error: JSON file not found: {file_path}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        print(f"Invalid JSON format: {error}")
        return False

    except OSError as error:
        print(f"Unable to read JSON file: {error}")
        return False

    print("JSON syntax is valid!")

    if not isinstance(data, dict):
        print("Error: JSON root must be an object!")
        return False

    # Required GMRID fields
    required_fields = [
        "record_id",
        "source",
        "article",
        "metadata",
        "entities",
        "relationships",
        "detected_risks",
        "severity_note"
    ]

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return print_errors(errors)

    # Validate record ID
    record_id = data["record_id"]

    if not (
        isinstance(record_id, int)
        and not isinstance(record_id, bool)
    ) and not (
        isinstance(record_id, str) and record_id.strip()
    ):
        errors.append("record_id must be an integer or non-empty string!")

    # Validate source and article
    for field in ["source", "article"]:
        if not isinstance(data[field], str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string!")

    if not isinstance(data["severity_note"], str):
        errors.append("severity_note must be a string!")

    # Validate metadata
    validate_metadata(data["metadata"], errors)

    # Validate NLP arrays
    for field in ["entities", "relationships", "detected_risks"]:
        if not isinstance(data[field], list):
            errors.append(f"{field} must be a list!")

    if errors:
        return print_errors(errors)

    # Validate nested NLP data
    entity_names, entity_types = validate_entities(
        data["entities"],
        errors
    )

    validate_relationships(
        data["relationships"],
        entity_names,
        errors
    )

    validate_detected_risks(
        data["detected_risks"],
        entity_types,
        entity_names,
        errors
    )

    if errors:
        return print_errors(errors)

    print("GMRID record validation successful!")
    print("Metadata validation successful!")
    print("Entity validation successful!")
    print("Relationship validation successful!")
    print("Detected risk validation successful!")
    print("\nJSON validation successful!")

    return True


if __name__ == "__main__":

    json_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_JSON_FILE
    )

    if not json_file.is_absolute():
        json_file = Path.cwd() / json_file

    validate_json(json_file)
