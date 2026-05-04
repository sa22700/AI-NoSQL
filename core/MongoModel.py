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

def create_mongo_query(
    llm: Llama,
    question: str,
    collection_name: str,
    known_fields: list[str]
) -> dict:
    fields_text = ", ".join(known_fields) if known_fields else "unknown"
    prompt = (
        "You are a MongoDB query JSON generator.\n"
        "Convert the user's question into one MongoDB read-only query JSON object.\n"
        "\n"
        "Return ONLY valid JSON.\n"
        "Do not explain anything.\n"
        "Do not use markdown.\n"
        "Do not wrap the JSON in code fences.\n"
        "Do not return JavaScript or mongosh syntax.\n"
        "\n"
        "Allowed operations:\n"
        "- find\n"
        "- count_documents\n"
        "\n"
        "Forbidden operations:\n"
        "- insert\n"
        "- update\n"
        "- delete\n"
        "- drop\n"
        "- aggregate\n"
        "\n"
        "Forbidden keys:\n"
        "- $where\n"
        "- $out\n"
        "- $merge\n"
        "- any key starting with $\n"
        "\n"
        "Use only exact value matching.\n"
        "Do not use MongoDB operators.\n"
        "Use only known fields.\n"
        "\n"
        f"Current collection: {collection_name}\n"
        f"Known fields: {fields_text}\n"
        "\n"
        "Required JSON format for find:\n"
        "{\n"
        '  "operation": "find",\n'
        '  "filter": {},\n'
        '  "projection": {},\n'
        "}\n"
        "\n"
        "Required JSON format for count_documents:\n"
        "{\n"
        '  "operation": "count_documents",\n'
        '  "filter": {}\n'
        "}\n"
        "\n"
        "Rules:\n"
        "- If the user asks what is inside the document, return all documents.\n"
        "- If the user asks to show all documents, return all documents.\n"
        "- If the user writes only a known field name, return that field using projection.\n"
        "- If the user asks how many documents there are, use count_documents.\n"
        "- If the question cannot be mapped safely, return all documents with find.\n"
    )
    full_prompt = (
        f"{prompt}\n"
        f"Question: {question}\n"
        f"JSON:\n"
    )
    output = llm(
        full_prompt,
        max_tokens=256,
        temperature=0.0,
        echo=False,
        stop=["```", "\n\nQuestion:", "\n\nAnswer:"]
    )
    raw_output = output["choices"][0]["text"].strip()
    raw_output = clean_ai_response(raw_output)
    query = json.loads(raw_output)
    return validate_query(query, known_fields)