import json
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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROMPT_TXT = os.getenv("PROMPT_TXT")
    PROMPT_PATH = os.path.join(BASE_DIR, "prompt", PROMPT_TXT)
    fields_text = ", ".join(known_fields) if known_fields else "unknown"
    with open (PROMPT_PATH, "r", encoding="utf-8") as file:
        temp = file.read()
    return (
        temp.replace("{{COLLECTION_NAME}}", collection_name)
        .replace("{{KNOWN_FIELDS}}", fields_text)
    )

def parse_model_query(raw_output: str, known_fields: list[str]) -> dict | None:
    decoder = json.JSONDecoder()
    position = 0
    valid_queries = []
    while position < len(raw_output):
        while position < len(raw_output) and raw_output[position].isspace():
            position += 1
        if position >= len(raw_output):
            break
        try:
            parsed, next_position = decoder.raw_decode(raw_output, position)
            position = next_position
            if isinstance(parsed, dict):
                try:
                    validated = validate_query(parsed, known_fields)
                    valid_queries.append(validated)

                except ValueError:
                    pass

        except json.JSONDecodeError:
            position += 1

    if not valid_queries:
        return None
    return valid_queries[-1]

def create_mongo_query(
    llm: Llama,
    question: str,
    collection_name: str,
    known_fields: list[str]
) -> dict | None:
    prompt = build_prompt(collection_name, known_fields)
    full_prompt = (
        f"{prompt}\n"
        f"Question: {question}\n"
        f"JSON:"
    )
    output = llm(
        full_prompt,
        max_tokens=256,
        temperature=0.0,
        echo=False,
        stop=["\n\nQuestion:", "\n\nAnswer:"]
    )
    raw_output = output["choices"][0]["text"].strip()
    raw_output = clean_ai_response(raw_output)
    try:
        query = parse_model_query(raw_output, known_fields)
        if query is None:
            print("Model did not return valid query JSON")
            print(f"Raw model output: {repr(raw_output)}")
            return None
        return query

    except json.JSONDecodeError:
        print("Model did not return valid JSON")
        print(f"Raw model output: {repr(raw_output)}")
        return None

    except ValueError as error:
        print(f"Invalid query: {error}")
        print(f"Raw model output: {repr(raw_output)}")
        return None

