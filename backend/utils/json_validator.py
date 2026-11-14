
import json
from pathlib import Path

# Locate the sample article JSON file
BASE_DIR = Path(__file__).resolve().parents[1]
FILE_PATH = BASE_DIR / "data" / "articles" / "sample_article.json"


def validate_json():

    # Check whether the file exists
    if not FILE_PATH.exists():
        print("Error: JSON file not found!")
        return

    try:
        # Read and parse JSON
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        print("JSON syntax is valid!")

        # Check required fields
        required_fields = [
            "article",
            "entities",
            "relationships",
            "detected_risks",
            "severity_note"
        ]

        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return

        # Check basic data types
        if not isinstance(data["article"], str):
            print("Error: article must be a string!")
            return

        for field in ["entities", "relationships", "detected_risks"]:
            if not isinstance(data[field], list):
                print(f"Error: {field} must be a list!")
                return

        print("All required fields are present!")
        print("JSON validation successful!")

    except json.JSONDecodeError as error:
        print("Invalid JSON format!")
        print(error)


if __name__ == "__main__":
    validate_json()
