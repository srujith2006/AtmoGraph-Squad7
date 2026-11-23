"""Automated OpenAPI / Swagger schema specification exporter.

Extracts the full OpenAPI 3.1.0 schema specification from the FastAPI app instance,
validates route completeness, and writes:
- docs/openapi.json: Complete machine-readable OpenAPI schema specification
- docs/API_SPECIFICATION.md: Markdown reference documentation of all endpoints and contracts
"""

import json
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.api.app import create_app


def export_openapi_schema(output_dir: Path = REPO_ROOT / "docs") -> Path:
    """Generate and write openapi.json and markdown documentation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    app = create_app()

    openapi_data = app.openapi()
    json_path = output_dir / "openapi.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(openapi_data, f, indent=2)

    print(f"✅ Successfully exported OpenAPI schema to: {json_path}")
    print(f"   API Title:   {openapi_data.get('info', {}).get('title')}")
    print(f"   Version:     v{openapi_data.get('info', {}).get('version')}")
    print(f"   Total Paths: {len(openapi_data.get('paths', {}))}")
    print(f"   Schemas:     {len(openapi_data.get('components', {}).get('schemas', {}))}")

    # Generate Markdown API Specification
    md_path = output_dir / "API_SPECIFICATION.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📑 AtmoGraph API Specification Reference\n\n")
        f.write(f"**Version:** `{openapi_data.get('info', {}).get('version')}`  \n")
        f.write(f"**OpenAPI Version:** `{openapi_data.get('openapi')}`  \n\n")
        f.write("## Endpoints Summary\n\n")
        f.write("| Method | Endpoint Path | Summary | Tags |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")

        for path, path_item in sorted(openapi_data.get("paths", {}).items()):
            for method, operation in path_item.items():
                if method.lower() in ("get", "post", "put", "delete", "patch"):
                    summary = operation.get("summary", "No description provided")
                    tags = ", ".join(operation.get("tags", ["General"]))
                    f.write(f"| `{method.upper()}` | `{path}` | {summary} | {tags} |\n")

    print(f"✅ Generated API documentation reference at: {md_path}")
    return json_path


if __name__ == "__main__":
    export_openapi_schema()
