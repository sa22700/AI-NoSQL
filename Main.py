# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from getpass import getpass
from core.Database import (
    create_client,
    get_collection,
    list_databases,
    list_collections
)
from core.Login import ensure_first_user, login_user
from core.Model import load_model
from core.Menu import run_main_menu

def main() -> None:
    client = create_client()
    print("Databases:")
    print(list_databases(client))
    database_name = input("Create/select database: ").strip()
    ensure_first_user(client, database_name)
    current_user = None
    while current_user is None:
        username = input("Enter username: ").strip()
        password = getpass("Enter password: ").strip()
        current_user = login_user(
            client=client,
            database_name=database_name,
            username=username,
            password=password
        )
        if current_user is None:
            print("Invalid username or password")
    print("Login successful")
    print("Collections:")
    print(list_collections(client, database_name))
    collection_name = input("Create/select collection: ").strip()
    collection = get_collection(
        client=client,
        database_name=database_name,
        collection_name=collection_name
    )
    print("Loading model...")
    llm = load_model()
    print("Model loaded")
    run_main_menu(
        client=client,
        database_name=database_name,
        collection_name=collection_name,
        collection=collection,
        llm=llm,
        current_user=current_user
    )

if __name__ == "__main__":
    main()