# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from getpass import getpass
from core.Actions import ask_database
from core.Database import (
    create_client,
    get_collection,
    list_collections,
    list_databases
)
from core.Documents import (
    add_document,
    delete_document,
    drop_collection,
    get_known_fields,
    update_document
)
from core.Input import (
    create_document_from_input,
    create_update_fields_from_input,
    create_user_from_input,
    select_document_filter,
    select_user_filter
)
from core.Login import ensure_first_user, login_user
from core.Menu import print_main_menu
from core.Model import load_model
from core.Users import add_user, delete_user, get_users


def main() -> None:
    client = create_client()
    try:
        print(list_databases(client))
        database_name = input("Create/select database: ").strip()
        ensure_first_user(client, database_name)
        while True:
            username = input("Enter username: ").strip()
            password = getpass("Enter password: ").strip()
            current_user = login_user(client, database_name, username, password)
            if current_user is not None:
                print("Login successful")
                break
            print("Invalid username or password")
        is_admin = current_user.get("is_admin", False)
        print(list_collections(client, database_name))
        collection_name = input("Create/select collection: ").strip()
        if collection_name == "users" and not is_admin:
            print("Only admin users can access users collection.")
            return
        collection = get_collection(
            client=client,
            database_name=database_name,
            collection_name=collection_name
        )
        print("Loading model...")
        llm = load_model()
        print("Model loaded.")
        while True:
            print_main_menu()
            choice = input("Select: ").strip()
            if choice == "1":
                document = create_document_from_input()
                add_document(collection, document)
            elif choice == "2":
                ask_database(llm, collection, collection_name)
            elif choice == "3":
                fields = get_known_fields(collection)
                print(fields)
            elif choice == "4":
                is_admin = current_user.get("is_admin", False)
                if not is_admin:
                    print("Only admin can add users.")
                    continue
                user = create_user_from_input()
                if user is not None:
                    add_user(client, database_name, user)
            elif choice == "5":
                is_admin = current_user.get("is_admin", False)
                if not is_admin:
                    print("Only admin can delete documents.")
                    continue
                print("Delete filter:")
                filtered = select_document_filter(collection)
                if filtered is not None:
                    delete_document(client, database_name, collection_name, filtered)
            elif choice == "6":
                is_admin = current_user.get("is_admin", False)
                if not is_admin:
                    print("Only admin can drop collections.")
                    continue
                drop_collection(client, database_name, collection_name)
                print(list_collections(client, database_name))
                collection_name = input("Create/select collection: ").strip()
                if not collection_name:
                    print("Collection name cannot be empty")
                    continue
                if collection_name == "users" and not is_admin:
                    print("Only admin users can access users collection.")
                    continue
                collection = get_collection(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name
                )
            elif choice == "7":
                filtered = select_document_filter(collection)
                if filtered is None:
                    continue
                print("Update fields:")
                update = create_update_fields_from_input()
                if update:
                    update_document(client, database_name, collection_name, filtered, update)
                else:
                    print("Empty update was not executed")
            elif choice == "8":
                is_admin = current_user.get("is_admin", False)
                if not is_admin:
                    print("Only admin can get users list.")
                    continue
                get_users(client, database_name)
            elif choice == "9":
                is_admin = current_user.get("is_admin", False)
                if not is_admin:
                    print("Only admin can delete users.")
                    continue
                print("Delete user:")
                filter_query = select_user_filter(client, database_name)
                if filter_query is not None:
                    delete_user(client, database_name, filter_query)
            elif choice == "0":
                break
            else:
                print("Unknown selection")

    finally:
        client.close()

if __name__ == "__main__":
    main()