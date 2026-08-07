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