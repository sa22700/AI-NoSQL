# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json

def parse_simple_document(text: str) -> dict:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON: {error.msg}"
        ) from error

    if not isinstance(document, dict) or not document:
        raise ValueError(
            "Document must be a non-empty JSON object"
        )

    if any(key.startswith("$") for key in document):
        raise ValueError(
            "Field name cannot start with $"
        )

    return document