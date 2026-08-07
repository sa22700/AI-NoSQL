# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from bson.json_util import loads
from pymongo.errors import PyMongoError
from core.Database import get_collection

def execute_query(collection, query: str) -> dict:
    try:
        filter_query = loads(query)
        if not isinstance(filter_query, dict):
            return {
                "ok": False,
                "result": [],
                "error": "MongoDB query must be an object",
            }
        results = list(collection.find(filter_query))
        for document in results:
            if "_id" in document:
                document["_id"] = str(document["_id"])
        return {
            "ok": True,
            "result": results,
            "error": None,
        }

    except (ValueError, TypeError) as error:
        return {
            "ok": False,
            "result": [],
            "error": f"Invalid MongoDB query: {error}",
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "result": [],
            "error": str(error),
        }

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
            safe_document["_id"] = str(
                safe_document["_id"]
            )
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
        result = collection.update_one(filter_query, {"$set": update_fields})
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
        for document in collection.find({}):
            for key in document.keys():
                if key != "_id":
                    fields.add(key)

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

    return sorted(fields)