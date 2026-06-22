# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os

MONGO_URI = os.getenv("MONGO_URI")
LLM_MODEL = os.getenv("LLM_MODEL")
READ_ONLY_MODE = True
ALLOWED_OPERATIONS = {
    "find",
    "count_documents",
    "find_by_value",
    "search_documents"
}
FORBIDDEN_KEYS = {
    "$where",
    "$out",
    "$merge",
    "$function",
    "$accumulator",
    "$regex",
    "$expr",
    "$jsonSchema",
    "$lookup",
    "$graphLookup",
    "$unionWith",
    "$text",
    "$near",
    "$nearSphere",
    "$geoNear"
}
ALLOWED_VALUE_TYPES = (
    str,
    int,
    float,
    bool,
    type(None)
)