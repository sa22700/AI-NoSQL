# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

MONGO_URI = "mongodb://100.109.50.66:27017/"
LLM_MODEL = "./unsloth.Q5_K_M.gguf"
READ_ONLY_MODE = True
ALLOWED_OPERATIONS = {
    "find",
    "count_documents",
    "find_by_value"
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