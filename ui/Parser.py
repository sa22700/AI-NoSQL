def parse_simple_document(text: str) -> dict:
    document = {}
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for part in line.split(","):
            part = part.strip()
            if part:
                parts.append(part)
    for part in parts:
        if ":" not in part:
            raise ValueError(f"Invalid field: {part}")
        key, value = part.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError("Field name cannot be empty")
        if key.startswith("$"):
            raise ValueError("Field name cannot start with $")
        document[key] = str(value)
    if not document:
        raise ValueError("Document cannot be empty")
    return document