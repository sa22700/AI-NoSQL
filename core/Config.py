# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
LLM_MODEL = os.getenv("LLM_MODEL")

FORBIDDEN_TOKENS = {
    "$where",
    "$function",
    "$accumulator",
    "$out",
    "$merge",
}