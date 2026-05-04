import json
from llama_cpp import Llama
from core.ModelSet import clean_ai_response, validate_query
from core.Connect import cuda_available, estimate_n_gpu_layers

def load_model() -> Llama:
    vram_gb = cuda_available()
    n_gpu_layers = estimate_n_gpu_layers(vram_gb)
    return Llama(
        model_path="./unsloth.Q5_K_M.gguf",
        use_mmap=False,
        n_gpu_layers=n_gpu_layers,
        n_ctx=4096,
        verbose=False
    )

def build_prompt(collection_name: str, known_fields: list[str]) -> str:
    fields_text = ", ".join(known_fields) if known_fields else "unknown"
    return (
        "You are a MongoDB query JSON generator.\n"
        "Convert the user's question into one read-only MongoDB query.\n"
        "Return only one valid JSON object. No markdown. No explanations.\n"
        "\n"
        "Allowed operations: find, count_documents.\n"
        "Forbidden operations: insert, update, delete, drop, aggregate.\n"
        "Forbidden keys: any key starting with $.\n"
        "\n"
        "Rules:\n"
        "- Use only exact value matching.\n"
        "- Use only known fields.\n"
        "- Words like show, list and find are commands, not field values.\n"
        "- If the user asks to show all, return all documents.\n"
        "- If the user writes only a known field name, return that field using projection.\n"
        "- If the user asks how many documents there are, use count_documents.\n"
        "- If unsure, return all documents using find.\n"
        "\n"
        f"Current collection: {collection_name}\n"
        f"Known fields: {fields_text}\n"
        "\n"
        "Output formats:\n"
        '{"operation":"find",'
        '"filter":{},'
        '"projection":{}}\n'
        '{"operation":"count_documents",'
        '"filter":{}}\n'
        "\n"
    )

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
        query = json.loads(raw_output)
        return validate_query(query, known_fields)

    except json.JSONDecodeError:
        print("Model did not return valid JSON")
        print(f"Raw model output: {repr(raw_output)}")
        return None

    except ValueError as error:
        print(f"Invalid query: {error}")
        print(f"Raw model output: {repr(raw_output)}")
        return None