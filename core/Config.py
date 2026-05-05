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
