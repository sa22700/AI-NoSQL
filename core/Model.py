# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
from llama_cpp import Llama
from core.Config import LLM_MODEL
from core.ModelSet import clean_ai_response, validate_query

def load_model() -> Llama:
    return Llama(
        model_path=LLM_MODEL,
        use_mmap=True,
        n_gpu_layers=-1,
        n_ctx=4096,
        use_mlock=True,
        verbose=False
    )

def build_prompt(collection_name: str, known_fields: list[str]) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_txt = os.getenv("PROMPT_TXT")
    prompt_path = os.path.join(base_dir, "prompt", prompt_txt)
    fields_text = (", ".join(known_fields) if known_fields else "unknown")
    with open(prompt_path, "r", encoding="utf-8") as file:
        temp = file.read()
    return (temp.replace("{{COLLECTION_NAME}}", collection_name)
        .replace("{{KNOWN_FIELDS}}",fields_text))

def create_mongo_query(
    llm: Llama,
    question: str,
    collection_name: str,
    known_fields: list[str]
) -> str | None:
    prompt = build_prompt(collection_name, known_fields)
    full_prompt = (
        f"{prompt}\n"
        f"Question: {question}\n"
        f"MongoDB query:"
    )
    output = llm(
        full_prompt,
        max_tokens=256,
        temperature=0.0,
        echo=False,
        stop=["\n\nQuestion:", "\n\nAnswer:"]
    )
    raw_output = (output["choices"][0]["text"].strip())
    query = clean_ai_response(raw_output)
    try:
        return validate_query(query, collection_name, known_fields)

    except ValueError as error:
        print(f"Invalid query: {error}")
        print(f"Raw model output: {repr(raw_output)}")
        return None