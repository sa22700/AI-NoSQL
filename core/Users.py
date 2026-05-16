# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from pymongo.errors import PyMongoError
from core.Database import get_collection

def add_user(
    client,
    database_name: str,
    user: dict
) -> dict:
    if not user:
        return {
            "ok": False,
            "username": None,
            "error": "Empty user was not added",
        }
    collection = get_collection(client, database_name, "users")
    username = user.get("username")
    if not username:
        return {
            "ok": False,
            "username": None,
            "error": "Username is missing",
        }
    try:
        existing_user = collection.find_one({"username": username})
        if existing_user is not None:
            return {
                "ok": False,
                "username": username,
                "error": "User already exists",
            }
        result = collection.insert_one(user)
        return {
            "ok": True,
            "inserted_id": str(result.inserted_id),
            "username": username,
            "error": None,
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "username": username,
            "error": str(error),
        }

def delete_user(
    client,
    database_name: str,
    filter_query: dict
) -> dict:
    if not filter_query:
        return {
            "ok": False,
            "deleted_count": 0,
            "error": "Empty filter is not allowed for delete",
        }
    collection = get_collection(client, database_name, "users")
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

def get_users(client, database_name: str) -> list[dict]:
    collection = get_collection(client, database_name, "users")
    try:
        users = list(collection.find({}, {"password": 0}))
        for user in users:
            if "_id" in user:
                user["_id"] = str(user["_id"])
        return users

    except PyMongoError:
        return []