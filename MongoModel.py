import json
from llama_cpp import Llama
from ModelSet import clean_ai_response, validate_query
from Connect import cuda_available, estimate_n_gpu_layers

READ_ONLY_MODE = True
ALLOWED_OPERATIONS = {
    "find",
    "count_documents"
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

def load_model() -> Llama:
    vram_gb = cuda_available()
    if vram_gb > 0:
        n_gpu_layers = estimate_n_gpu_layers(vram_gb)
    else:
        n_gpu_layers = 0
    return Llama(
        model_path="unsloth.Q5_K_M.gguf",
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
        "You are a MongoDB query generator.\n"
        "Return only valid JSON.\n"
        "Do not explain anything.\n"
        "Do not use markdown.\n"
        "Do not return JavaScript or mongosh syntax.\n"
        "Allowed operations: find, count_documents.\n"
        "Forbidden operations: insert, update, delete, drop, aggregate, $where, $out, $merge.\n"
        "Do not use MongoDB operators.\n"
        "Use only exact value matching.\n"
        f"Current collection: {collection_name}\n"
        f"Known fields: {fields_text}\n"
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