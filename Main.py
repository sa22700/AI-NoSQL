import json
from core.MongoDB import (
    create_client,
    get_collection,
    add_document,
    get_known_fields,
    execute_query
)
from core.MongoModel import load_model, create_mongo_query
from core.MongoUser import add_user
from core.MongoDel import delete_document
from core.MongoDrop import drop_collection
from core.MongoUpd import update_document

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
        execute_query(collection, query)

    except json.JSONDecodeError:
        print("Model did not return valid JSON")

    except ValueError as error:
        print(f"Rejected query: {error}")

def main() -> None:
    client = create_client()
    database_name = input("Create/select database: ")
    collection_name = input("Create/select collection: ")
    collection = get_collection(
        client=client,
        database_name=database_name,
        collection_name=collection_name
    )
    print("Loading model...")
    llm = load_model()
    print("Model loaded.")
    while True:
        print("\n1: Add document")
        print("2: Ask database")
        print("3: Show known fields")
        print("4: Add user")
        print("5: Delete document")
        print("6: Drop collection")
        print("7: Update document")
        print("0: Exit")
        choice = input("Select: ")
        if choice == "1":
            document = create_document_from_input()
            add_document(collection, document)
        elif choice == "2":
            ask_database(llm, collection, collection_name)
        elif choice == "3":
            fields = get_known_fields(collection)
            print(fields)
        elif choice == "4":
            user = create_document_from_input()
            add_user(client, database_name, collection_name, user)
        elif choice == "5":
            print("Delete filter:")
            filtered = create_document_from_input()
            delete_document(client, database_name, collection_name, filtered)
        elif choice == "6":
            drop_collection(client, database_name, collection_name)
        elif choice == "7":
            print("Update filter:")
            filtered = create_document_from_input()
            print("Update fields:")
            update = create_document_from_input()
            update_document(client, database_name, collection_name, filtered, update)
        elif choice == "0":
            break
        else:
            print("Unknown selection")
    client.close()

if __name__ == "__main__":
    main()