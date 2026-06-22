# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from pymongo.errors import PyMongoError
from core.Database import get_collection

def add_document(collection, document: dict) -> dict:
    if not document:
        return {
            "ok": False,
            "inserted_id": None,
            "document": None,
            "error": "Empty document was not added",
        }
    try:
        result = collection.insert_one(document)
        safe_document = dict(document)
        if "_id" in safe_document:
            safe_document["_id"] = str(safe_document["_id"])
        return {
            "ok": True,
            "inserted_id": str(result.inserted_id),
            "document": safe_document,
            "error": None,
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "inserted_id": None,
            "document": None,
            "error": str(error),
        }

def delete_document(
    client,
    database_name: str,
    collection_name: str,
    filter_query: dict
) -> dict:
    if not filter_query:
        return {
            "ok": False,
            "deleted_count": 0,
            "error": "Empty filter is not allowed for delete",
        }
    collection = get_collection(client, database_name, collection_name)
    try:
        result = collection.delete_one(filter_query)
        return {
            "ok": True,
            "filter": filter_query,
            "deleted_count": result.deleted_count,
            "error": None,
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "deleted_count": 0,
            "error": str(error),
        }

def update_document(
    client,
    database_name: str,
    collection_name: str,
    filter_query: dict,
    update_fields: dict
) -> dict:
    if collection_name.strip().lower() == "users":
        return {
            "ok": False,
            "matched_count": 0,
            "modified_count": 0,
            "error": "Updating users collection is not allowed",
        }
    if not filter_query:
        return {
            "ok": False,
            "matched_count": 0,
            "modified_count": 0,
            "error": "Empty filter is not allowed for update",
        }
    if not update_fields:
        return {
            "ok": False,
            "matched_count": 0,
            "modified_count": 0,
            "error": "Empty update was not applied",
        }
    collection = get_collection(client, database_name, collection_name)
    try:
        result = collection.update_one(
            filter_query,
            {"$set": update_fields}
        )
        return {
            "ok": True,
            "filter": filter_query,
            "updated": update_fields,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "error": None,
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "matched_count": 0,
            "modified_count": 0,
            "error": str(error),
        }

def drop_collection(
    client,
    database_name: str,
    collection_name: str,
    confirm: bool = False
) -> dict:
    if not confirm:
        return {
            "ok": False,
            "dropped": None,
            "error": "Confirmation required",
        }
    collection = get_collection(client, database_name, collection_name)
    try:
        collection.drop()
        return {
            "ok": True,
            "dropped": collection_name,
            "database": database_name,
            "error": None,
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "dropped": None,
            "error": str(error),
        }

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

def has_text_index(collection) -> bool:
    indexes = collection.index_information()
    for index_info in indexes.values():
        if "weights" in index_info:
            return True
        for _, direction in index_info.get("key", []):
            if direction == "text":
                return True
    return False

def ensure_text_search_index(collection) -> None:
    if has_text_index(collection):
        return
    collection.create_index(
        [("$**", "text")],
        name="ai_text_search",
        default_language="none"
    )

def make_document_safe(document: dict) -> dict:
    safe_document = dict(document)

    if "_id" in safe_document:
        safe_document["_id"] = str(safe_document["_id"])

    return safe_document

def execute_query(collection, query: dict) -> dict:
    operation = query.get("operation")
    filter_query = query.get("filter", {})
    projection = query.get("projection", {})
    try:
        if operation == "find":
            results = list(collection.find(filter_query, projection))
            for document in results:
                if "_id" in document:
                    document["_id"] = str(document["_id"])
            return {
                "ok": True,
                "result": results,
                "error": None,
            }
        if operation == "count_documents":
            count = collection.count_documents(filter_query)
            return {
                "ok": True,
                "result": [{"count": count}],
                "error": None,
            }
        if operation == "find_by_value":
            wanted_value = query.get("value")

            if wanted_value is None:
                return {
                    "ok": False,
                    "result": [],
                    "error": "Missing value",
                }
            results = []
            for document in collection.find({}):
                if document_contains_value(document, str(wanted_value)):
                    if "_id" in document:
                        document["_id"] = str(document["_id"])
                    results.append(document)
            return {
                "ok": True,
                "result": results,
                "error": None,
            }
        if operation == "search_documents":
            search_text = query.get("query")
            if not search_text:
                return {
                    "ok": False,
                    "result": [],
                    "error": "Missing search query",
                }
            ensure_text_search_index(collection)
            results = list(
                collection.find(
                    {
                        "$text": {
                            "$search": search_text
                        }
                    },
                    {
                        "score": {
                            "$meta": "textScore"
                        }
                    }
                )
                .sort([
                    ("score", {
                        "$meta": "textScore"
                    })
                ])
            )
            safe_results = []

            for document in results:
                safe_document = make_document_safe(document)
                safe_results.append(safe_document)

            return {
                "ok": True,
                "result": safe_results,
                "error": None,
            }
        return {
            "ok": False,
            "result": [],
            "error": "Unsupported operation",
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "result": [],
            "error": str(error),
        }