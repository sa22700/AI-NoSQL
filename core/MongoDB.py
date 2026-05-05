import json
import pymongo
from pymongo.errors import PyMongoError

def create_client() -> pymongo.MongoClient:
    return pymongo.MongoClient("mongodb://192.168.68.109:27017/")

def get_collection(client, database_name: str, collection_name: str) -> pymongo.collection.Collection:
    db = client[database_name]
    return db[collection_name]

def list_databases(client) -> list[str]:
    system_databases = {"admin", "config", "local"}
    return [database_name
            for database_name in client.list_database_names()
            if database_name not in system_databases]

def list_collections(client, database_name: str) -> list[str]:
    db = client[database_name]
    return db.list_collection_names()

def add_document(collection, document: dict) -> None:
    if not document:
        print("Empty document was not added")
        return
    try:
        result = collection.insert_one(document)
        print("Document added:")
        print(json.dumps({
            "inserted_id": str(result.inserted_id),
            "document": document
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

def get_known_fields(collection) -> list[str]:
    fields = set()
    try:
        for document in collection.find({}).limit(20):
            for key in document.keys():
                if key != "_id":
                    fields.add(key)

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

    return sorted(fields)

def document_contains_value(document: dict, wanted_value: str) -> bool:
    for key, value in document.items():
        if key == "_id":
            continue
        if isinstance(value, dict):
            if document_contains_value(value, wanted_value):
                return True
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if document_contains_value(item, wanted_value):
                        return True
                elif str(item) == wanted_value:
                    return True
        elif str(value) == wanted_value:
            return True
    return False

def execute_query(collection, query: dict) -> None:
    operation = query.get("operation")
    filter_query = query.get("filter", {})
    projection = query.get("projection", {})
    try:
        if operation == "find":
            results = collection.find(filter_query, projection)
            found = False
            for index, document in enumerate(results, start=1):
                found = True
                print(f"\n{index}:")
                print(json.dumps(document, indent=2, ensure_ascii=False, default=str))
            if not found:
                print("No documents found")
        elif operation == "count_documents":
            count = collection.count_documents(filter_query)
            print(f"Count: {count}")
        elif operation == "find_by_value":
            wanted_value = query.get("value")
            if wanted_value is None:
                print("Missing value")
                return
            results = collection.find({})
            found = False
            for index, document in enumerate(results, start=1):
                if document_contains_value(document, str(wanted_value)):
                    found = True
                    print(f"\n{index}:")
                    print(json.dumps(document, indent=2, ensure_ascii=False, default=str))
            if not found:
                print("No documents found")
        else:
            print("Unsupported operation")

    except PyMongoError as error:
        print(f"MongoDB error: {error}")