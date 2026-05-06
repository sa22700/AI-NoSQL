# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json
from pymongo.errors import PyMongoError
from core.Database import get_collection

def add_user(
    client,
    database_name: str,
    user: dict
) -> None:
    if not user:
        print("Empty user was not added")
        return
    collection = get_collection(client, database_name, "users")
    username = user.get("username")
    if not username:
        print("Username is missing")
        return
    try:
        existing_user = collection.find_one({"username": username})
        if existing_user is not None:
            print("User already exists")
            return
        result = collection.insert_one(user)
        print("User added:")
        print(json.dumps({
            "inserted_id": str(result.inserted_id),
            "username": username
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

def delete_user(
    client,
    database_name: str,
    filter_query: dict
) -> None:
    if not filter_query:
        print("Empty filter is not allowed for delete")
        return
    collection = get_collection(client, database_name, "users")
    try:
        result = collection.delete_one(filter_query)
        print("User delete result:")
        print(json.dumps({
            "filter": filter_query,
            "deleted_count": result.deleted_count
        }, indent=2, ensure_ascii=False, default=str))

    except PyMongoError as error:
        print(f"MongoDB error: {error}")

def get_users(client, database_name: str) -> list[dict]:
    collection = get_collection(client, database_name, "users")
    try:
        users = list(collection.find({}, {"password": 0}))
        if not users:
            print("No users found.")
            return []
        print("Users:")
        for index, user in enumerate(users, start=1):
            print(f"\n{index}:")
            print(json.dumps(user, indent=2, ensure_ascii=False, default=str))
        return users

    except PyMongoError as error:
        print(f"MongoDB error: {error}")
        return []