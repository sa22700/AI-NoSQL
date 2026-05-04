import json
import pymongo
from pymongo.errors import PyMongoError

def create_client():
    return pymongo.MongoClient("mongodb://192.168.68.109:27017/")

def get_collection(client, database_name: str, collection_name: str):
    db = client[database_name]
    return db[collection_name]

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

def execute_query(collection, query: dict) -> None:
    operation = query.get("operation")
    filter_query = query.get("filter", {})
    projection = query.get("projection", {})
    try:
        if operation == "find":
            results = collection.find(filter_query, projection).limit(20)
            found = False
            for document in results:
                found = True
                print(json.dumps(document, indent=2, ensure_ascii=False, default=str))
            if not found:
                print("No documents found")
        elif operation == "count_documents":
            count = collection.count_documents(filter_query)
            print(f"Count: {count}")
        else:
            print("Unsupported operation")

    except PyMongoError as error:
        print(f"MongoDB error: {error}")