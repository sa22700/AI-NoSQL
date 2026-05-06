# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from core.Documents import (
    add_document,
    delete_document,
    update_document,
    drop_collection
)
from core.Users import (
    add_user,
    delete_user,
    get_users
)
from core.Actions import ask_database
from core.Input import (
    create_document_from_input,
    create_update_fields_from_input,
    create_user_from_input,
    select_document_filter,
    select_user_filter
)

def print_menu(is_admin: bool) -> None:
    print("\nMenu:")
    print("1. Add document")
    print("2. Ask database")
    print("3. Update document")
    print("4. Delete document")
    if is_admin:
        print("5. List users")
        print("6. Add user")
        print("7. Delete user")
        print("8. Drop collection")
    print("0. Exit")

def run_main_menu(
    client,
    database_name: str,
    collection_name: str,
    collection,
    llm,
    current_user: dict
) -> None:
    is_admin = bool(current_user.get("is_admin", False))
    while True:
        print_menu(is_admin)
        choice = input("Select option: ").strip()
        if choice == "1":
            document = create_document_from_input()
            add_document(collection, document)
        elif choice == "2":
            ask_database(llm, collection, collection_name)
        elif choice == "3":
            filter_query = select_document_filter(collection)
            if filter_query is None:
                continue
            update_fields = create_update_fields_from_input()
            update_document(
                client=client,
                database_name=database_name,
                collection_name=collection_name,
                filter_query=filter_query,
                update_fields=update_fields
            )
        elif choice == "4":
            filter_query = select_document_filter(collection)
            if filter_query is None:
                continue
            delete_document(
                client=client,
                database_name=database_name,
                collection_name=collection_name,
                filter_query=filter_query
            )
        elif choice == "5" and is_admin:
            get_users(client, database_name)
        elif choice == "6" and is_admin:
            user = create_user_from_input()
            if user is None:
                continue
            add_user(client, database_name, user)
        elif choice == "7" and is_admin:
            filter_query = select_user_filter(client, database_name)
            if filter_query is None:
                continue
            delete_user(client, database_name, filter_query)
        elif choice == "8" and is_admin:
            drop_collection(
                client=client,
                database_name=database_name,
                collection_name=collection_name
            )
            break
        elif choice == "0":
            print("Exit")
            break
        else:
            print("Invalid option")