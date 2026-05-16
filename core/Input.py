# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json
from getpass import getpass
from argon2 import PasswordHasher
from pymongo.errors import PyMongoError
from core.Database import get_collection

def create_document_from_input() -> dict:
    document = {}
    while True:
        field_name = input("Field name: ").strip()
        if field_name == "":
            break
        if field_name.startswith("$"):
            print("Field name cannot start with $")
            continue
        value = input("Value: ").strip()
        document[field_name] = value
    return document

def create_update_fields_from_input() -> dict:
    update_fields = {}
    while True:
        field_name = input("Field name: ").strip()
        if field_name == "":
            break
        if field_name.startswith("$"):
            print("Field name cannot start with $")
            continue
        value = input("New value: ").strip()
        update_fields[field_name] = value
    return update_fields

def create_user_from_input() -> dict | None:
    ph = PasswordHasher()
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty")
        return None
    if username.startswith("$"):
        print("Username cannot start with $")
        return None
    password = getpass("Password: ").strip()
    if not password:
        print("Password cannot be empty")
        return None
    confirm_password = getpass("Confirm Password: ").strip()
    if not confirm_password:
        print("Password cannot be empty")
        return None
    if password != confirm_password:
        print("Passwords do not match")
        return None
    password_hash = ph.hash(password)
    return {
        "username": username,
        "password": password_hash,
        "is_admin": False
    }

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

def select_user_filter(client, database_name: str) -> dict | None:
    collection = get_collection(client, database_name, "users")
    try:
        users = list(collection.find({}, {"password": 0}))
        if not users:
            print("No users found")
            return None
        print("Users:")
        for index, user in enumerate(users, start=1):
            safe_user = {
                "_id": user.get("_id"),
                "username": user.get("username"),
                "is_admin": user.get("is_admin", False)
            }
            print(f"\n{index}:")
            print(json.dumps(safe_user, indent=2, ensure_ascii=False, default=str))
        choice = input("Select user to delete: ").strip()
        if not choice.isdigit():
            print("Invalid selection")
            return None
        selected_index = int(choice)
        if selected_index < 1 or selected_index > len(users):
            print("Invalid selection")
            return None
        selected_user = users[selected_index - 1]
        confirm = input(
            f"Delete user '{selected_user.get('username')}'? yes/no: "
        ).strip().lower()
        if confirm != "yes":
            print("Delete cancelled")
            return None
        return {
            "_id": selected_user["_id"]
        }

    except PyMongoError as error:
        print(f"MongoDB error: {error}")
        return None

    except ValueError as error:
        print(f"MongoDB error: {error}")
        return None

    except KeyboardInterrupt as error:
        print(f"MongoDB error: {error}")
        return None