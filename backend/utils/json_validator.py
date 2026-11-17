
import json
import sys
from pathlib import Path

# Locate backend directory
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Default NLP JSON input file
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

# Allowed severity levels
SUPPORTED_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH"
}


def validate_json(file_path):
    """Validate NLP article JSON before Neo4j ingestion."""

    errors = []

    # Check file existence
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

    # Check root structure
    if not isinstance(data, dict):
        print("Error: JSON root must be an object!")
        return False

    required_fields = [
        "article",
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

    # Validate basic field types
    if not isinstance(data["article"], str):
        errors.append("article must be a string!")

    if not isinstance(data["severity_note"], str):
        errors.append("severity_note must be a string!")

    for field in ["entities", "relationships", "detected_risks"]:
        if not isinstance(data[field], list):
            errors.append(f"{field} must be a list!")

    if errors:
        return print_errors(errors)

    # Validate entities
    entity_names = set()
    entity_ids = set()
    entity_types = {}

    for index, entity in enumerate(data["entities"]):

        if not isinstance(entity, dict):
            errors.append(f"Entity {index + 1} must be an object!")
            continue

        name = entity.get("name")
        entity_type = entity.get("type")
        entity_id = entity.get("id")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"Entity {index + 1}: invalid or missing name!")
            continue

        if not isinstance(entity_type, str):
            errors.append(f"Entity {name}: missing or invalid type!")
            continue

        if entity_type not in SUPPORTED_ENTITY_TYPES:
            errors.append(
                f"Entity {name}: unsupported type '{entity_type}'!"
            )
            continue

        if entity_id is not None:
            if not isinstance(entity_id, str) or not entity_id.strip():
                errors.append(f"Entity {name}: ID must be a non-empty string!")
            elif entity_id in entity_ids:
                errors.append(f"Duplicate entity ID: {entity_id}")
            else:
                entity_ids.add(entity_id)

        normalized_name = name.strip()

        if normalized_name in entity_names:
            errors.append(f"Duplicate entity name: {normalized_name}")
        else:
            entity_names.add(normalized_name)
            entity_types[normalized_name] = entity_type

    # Validate relationships
    for index, relationship in enumerate(data["relationships"]):

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

    # Validate detected risks
    for index, risk in enumerate(data["detected_risks"]):

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

        if entity_types.get(risk_name.strip()) != "RISK":
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

    # Final result
    if errors:
        return print_errors(errors)

    print("All required fields are present!")
    print("Entity validation successful!")
    print("Relationship validation successful!")
    print("Detected risk validation successful!")
    print("\nJSON validation successful!")

    return True


def print_errors(errors):
    """Display validation errors."""

    print("\nJSON validation failed!")

    for error in errors:
        print(f"- {error}")

    return False


if __name__ == "__main__":

    # Accept custom JSON path or use default
    json_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_JSON_FILE
    )

    if not json_file.is_absolute():
        json_file = Path.cwd() / json_file

    validate_json(json_file)
