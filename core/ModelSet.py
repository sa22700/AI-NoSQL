from bson.json_util import loads
from core.Config import FORBIDDEN_TOKENS


def clean_ai_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def contains_forbidden_token(value) -> bool:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key in FORBIDDEN_TOKENS:
                return True
            if contains_forbidden_token(nested_value):
                return True
    elif isinstance(value, list):
        for item in value:
            if contains_forbidden_token(item):
                return True
    return False

def validate_query(
    query: str,
    collection_name: str
) -> str:
    if not query:
        raise ValueError("Query cannot be empty")
    try:
        parsed = loads(query)

    except ValueError as error:
        raise ValueError("Invalid MongoDB query") from error

    if not isinstance(parsed, dict):
        raise ValueError("MongoDB query must be an object")

    if contains_forbidden_token(parsed):
        raise ValueError("Query contains forbidden MongoDB operator")
    return query