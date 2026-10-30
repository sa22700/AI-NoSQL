# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from bson.json_util import loads

LOGICAL_OPERATORS = {"$and", "$or", "$nor"}
FIELD_OPERATORS = {
    "$eq", "$ne",
    "$gt", "$gte", "$lt", "$lte",
    "$in", "$nin", "$all",
    "$exists", "$type", "$size",
    "$regex", "$options",
    "$not", "$elemMatch",
}

def clean_ai_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def validate_literal(value) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.startswith("$"):
                raise ValueError(
                    f"Operator is not allowed here: {key}"
                )
            validate_literal(nested)
    elif isinstance(value, list):
        for item in value:
            validate_literal(item)

def validate_field(value, known_fields: set[str]) -> None:
    if not isinstance(value, dict):
        validate_literal(value)
        return
    operators = [key for key in value if key.startswith("$")]
    if not operators:
        validate_literal(value)
        return
    if len(operators) != len(value):
        raise ValueError("Mixed field values and operators")
    for operator, operand in value.items():
        if operator not in FIELD_OPERATORS:
            raise ValueError(
                f"Forbidden MongoDB operator: {operator}"
            )
        if operator == "$not":
            if not isinstance(operand, dict) or not operand:
                raise ValueError("Invalid $not condition")
            validate_field(operand, known_fields)
        elif operator == "$elemMatch":
            if not isinstance(operand, dict) or not operand:
                raise ValueError("Invalid $elemMatch condition")
            if all(key.startswith("$") for key in operand):
                if all(key in LOGICAL_OPERATORS for key in operand):
                    validate_filter(operand, known_fields, nested=True)
                else:
                    validate_field(operand, known_fields)
            else:
                validate_filter(operand, known_fields, nested=True)
        elif operator in {"$in", "$nin", "$all"}:
            if not isinstance(operand, list):
                raise ValueError(f"{operator} requires an array")
            validate_literal(operand)
        elif operator == "$exists":
            if not isinstance(operand, bool):
                raise ValueError("$exists requires a boolean")
        elif operator == "$size":
            if type(operand) is not int or operand < 0:
                raise ValueError("$size requires a nonnegative integer")
        elif operator == "$regex":
            if not isinstance(operand, str) or len(operand) > 256:
                raise ValueError("Invalid or oversized regex")
        elif operator == "$options":
            if "$regex" not in value or operand not in ("", "i"):
                raise ValueError("Invalid regex options")
        elif operator == "$type":
            if type(operand) not in (str, int):
                raise ValueError("Invalid $type value")
        else:
            validate_literal(operand)

def validate_filter(
    document: dict,
    known_fields: set[str],
    nested: bool = False
) -> None:
    if not isinstance(document, dict):
        raise ValueError("Filter must be a JSON object")
    for key, value in document.items():
        if key in LOGICAL_OPERATORS:
            if not isinstance(value, list) or not value:
                raise ValueError(f"Invalid {key} condition")
            for condition in value:
                validate_filter(condition, known_fields, nested)
        elif key.startswith("$"):
            raise ValueError(
                f"Forbidden MongoDB operator: {key}"
            )
        else:
            if not nested and key not in known_fields and key != "_id":
                raise ValueError(f"Unknown field: {key}")
            validate_field(value, known_fields)

def validate_query(
    query: str,
    collection_name: str,
    known_fields: list[str]
) -> str:
    if not query:
        raise ValueError("Query cannot be empty")
    try:
        parsed = loads(query)

    except (ValueError, TypeError) as error:
        raise ValueError("Invalid MongoDB query") from error

    if not isinstance(parsed, dict):
        raise ValueError("MongoDB query must be an object")
    validate_filter(parsed, set(known_fields))
    return query
