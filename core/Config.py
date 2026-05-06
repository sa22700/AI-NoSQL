# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os

MONGO_URI = "mongodb://192.168.68.109:27017/"
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
    "$accumulator"
}
ALLOWED_VALUE_TYPES = (
    str,
    int,
    float,
    bool,
    type(None)
)