# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json
from pymongo.errors import PyMongoError
from core.Database import get_collection

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

def delete_document(
    client,
    database_name: str,
    collection_name: str,
    filter_query: dict
) -> None:
    if not filter_query:
        print("Empty filter is not allowed for delete")
        return
    collection = get_collection(client, database_name, collection_name)
    try:
        result = collection.delete_one(filter_query)
        print("Document delete result:")
        print(json.dumps({
            "filter": filter_query,
            "deleted_count": result.deleted_count
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

def update_document(
    client,
    database_name: str,
    collection_name: str,
    filter_query: dict,
    update_fields: dict
) -> None:
    if not filter_query:
        print("Empty filter is not allowed for update")
        return
    if not update_fields:
        print("Empty update was not applied")
        return
    collection = get_collection(client, database_name, collection_name)
    try:
        result = collection.update_one(
            filter_query,
            {"$set": update_fields}
        )
        print("Document update result:")
        print(json.dumps({
            "filter": filter_query,
            "update": update_fields,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

def drop_collection(
    client,
    database_name: str,
    collection_name: str
) -> None:
    confirm = input(f"Type DROP to delete collection '{collection_name}': ").strip()
    if confirm != "DROP":
        print("Drop cancelled")
        return
    collection = get_collection(client, database_name, collection_name)
    try:
        collection.drop()
        print("Collection dropped:")
        print(json.dumps({
            "database": database_name,
            "collection": collection_name
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