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
    while True:
        admin_answer = input("Is admin (yes/no): ").strip().lower()
        if admin_answer == "yes":
            is_admin = True
            break
        elif admin_answer == "no":
            is_admin = False
            break
        print("Invalid input")
    return {
        "username": username,
        "password": password_hash,
        "is_admin": is_admin,
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

def update_user_filter(client, database_name: str) -> dict | None:
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
                "is_admin": user.get("is_admin", False),
            }
            print(f"\n{index}:")
            print(json.dumps(safe_user, indent=2, ensure_ascii=False, default=str))
        while True:
            choice = input("Select user to update: ").strip()
            if not choice.isdigit():
                print("Invalid selection")
                continue
            selected_index = int(choice)
            if selected_index < 1 or selected_index > len(users):
                print("Invalid selection")
                continue
            selected_user = users[selected_index - 1]
            return {
                "_id": selected_user["_id"],
            }

    except PyMongoError as error:
        print(f"MongoDB error: {error}")
        return None

    except ValueError as error:
        print(f"Value error: {error}")
        return None

    except KeyboardInterrupt:
        print("Update cancelled")
        return None

def create_user_update_from_input() -> dict:
    ph = PasswordHasher()
    update_fields = {}
    new_username = input("New username, leave empty to keep current: ").strip()
    if new_username:
        if new_username.startswith("$"):
            print("Username cannot start with $")
            return {}
        update_fields["username"] = new_username
    while True:
        password_answer = input("Change password (yes/no): ").strip().lower()
        if password_answer == "yes":
            password = getpass("Password: ")
            if not password:
                print("Password cannot be empty")
                return {}
            confirm_password = getpass("Confirm Password: ")
            if not confirm_password:
                print("Password cannot be empty")
                return {}
            if password != confirm_password:
                print("Passwords do not match")
                return {}
            update_fields["password"] = ph.hash(password)
            break
        elif password_answer == "no":
            break
        print("Invalid input")
    while True:
        admin_answer = input("Change admin rights (yes/no): ").strip().lower()
        if admin_answer == "yes":
            while True:
                new_admin_answer = input("Is admin (yes/no): ").strip().lower()
                if new_admin_answer == "yes":
                    update_fields["is_admin"] = True
                    break
                elif new_admin_answer == "no":
                    update_fields["is_admin"] = False
                    break
                print("Invalid input")
            break
        elif admin_answer == "no":
            break
        print("Invalid input")
    return update_fields