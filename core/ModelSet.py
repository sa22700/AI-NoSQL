# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from core.Config import (
    FORBIDDEN_KEYS,
    ALLOWED_VALUE_TYPES,
    READ_ONLY_MODE,
    ALLOWED_OPERATIONS
)

def clean_ai_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "")
        return text.strip()
    if text.startswith("```"):
        text = text.replace("```", "")
        return text.strip()
    return text

def contains_forbidden_key(value) -> bool:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key in FORBIDDEN_KEYS:
                return True
            if key.startswith("$"):
                return True
            if contains_forbidden_key(nested_value):
                return True
    elif isinstance(value, list):
        for item in value:
            if contains_forbidden_key(item):
                return True
    return False

def validate_filter_fields(filter_query: dict, known_fields: list[str]) -> dict:
    if not known_fields:
        return
    allowed_fields = set(known_fields)
    allowed_fields.add("_id")
    for key, value in filter_query.items():
        if key.startswith("$"):
            raise ValueError("MongoDB operators are not allowed")
        if key not in allowed_fields:
            raise ValueError(f"Unknown field: {key}")
        if not isinstance(value, ALLOWED_VALUE_TYPES):
            raise ValueError(f"Only exact value matching is allowed for field: {key}")

def validate_projection_fields(projection: dict, known_fields: list[str]) -> dict:
    if not known_fields:
        return
    allowed_fields = set(known_fields)
    allowed_fields.add("_id")
    for key, value in projection.items():
        if key.startswith("$"):
            raise ValueError("MongoDB operators are not allowed in projection")
        if key not in allowed_fields:
            raise ValueError(f"Unknown projection field: {key}")
        if value not in (0, 1, True, False):
            raise ValueError(f"Invalid projection value for field: {key}")

def validate_query(query: dict, known_fields: list[str]) -> dict:
    if not isinstance(query, dict):
        raise ValueError("Query must be a JSON object")
    operation = query.get("operation")
    filter_query = query.get("filter", {})
    projection = query.get("projection", {})
    if READ_ONLY_MODE and operation not in ALLOWED_OPERATIONS:
        raise ValueError("Operation is not allowed in read-only mode")
    if not isinstance(filter_query, dict):
        raise ValueError("Filter must be an object")
    if not isinstance(projection, dict):
        raise ValueError("Projection must be an object")
    if contains_forbidden_key(query):
        raise ValueError("Query contains forbidden MongoDB operator")
    if operation == "search_documents":
        return validate_search_documents_query(query)
    validate_filter_fields(filter_query, known_fields)
    validate_projection_fields(projection, known_fields)
    return query

def validate_search_documents_query(query: dict) -> dict:
    search_text = query.get("query")
    if search_text is None:
        search_text = query.get("value")
    if not isinstance(search_text, str):
        raise ValueError("Search query must be a string")
    search_text = search_text.strip()
    if not search_text:
        raise ValueError("Search query cannot be empty")
    filter_query = query.get("filter", {})
    projection = query.get("projection", {})
    if filter_query not in ({}, None):
        raise ValueError("search_documents does not allow custom filters")
    if projection not in ({}, None):
        raise ValueError("search_documents does not allow custom projections")
    return {
        "operation": "search_documents",
        "query": search_text,
        "filter": {},
        "projection": {}
    }