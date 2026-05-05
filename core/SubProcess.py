import json
from core.MongoDB import get_known_fields, execute_query
from core.MongoModel import create_mongo_query

def create_document_from_input() -> dict:
    document = {}
    while True:
        field_name = input("Field name: ")
        if field_name == "":
            break
        if field_name.startswith("$"):
            print("Field name cannot start with $")
            continue
        value = input("Value: ")
        document[field_name] = value
    return document

def select_document_filter(collection) -> dict | None:
    documents = list(collection.find({}))
    if not documents:
        print("No documents found")
        return None
    for index, document in enumerate(documents, start=1):
        print(f"\n{index}:")
        print(json.dumps(document, indent=2, ensure_ascii=False, default=str))
    choice = input("Select document: ").strip()
    if not choice.isdigit():
        print("Invalid selection")
        return None
    selected_index = int(choice)
    if selected_index < 1 or selected_index > len(documents):
        print("Invalid selection")
        return None
    selected_document = documents[selected_index - 1]
    return {
        "_id": selected_document["_id"]
    }

def ask_database(llm, collection, collection_name: str) -> None:
    known_fields = get_known_fields(collection)
    if not known_fields:
        print("Collection has no known fields yet. Add at least one document first.")
        return
    question = input("Question: ")
    try:
        query = create_mongo_query(
            llm=llm,
            question=question,
            collection_name=collection_name,
            known_fields=known_fields
        )
        print("Generated query:")
        print(json.dumps(query, indent=2, ensure_ascii=False))
        print("Result:")
        if query is None:
            print("Query was not executed because model output was invalid")
            return
        execute_query(collection, query)

    except json.JSONDecodeError:
        print("Model did not return valid JSON")

    except ValueError as error:
        print(f"Rejected query: {error}")