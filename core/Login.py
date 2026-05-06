# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from getpass import getpass
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from core.Database import get_collection

def ensure_first_user(client, database_name: str) -> None:
    collection = get_collection(client, database_name, "users")
    user_count = collection.count_documents({})
    if user_count > 0:
        return
    ph = PasswordHasher()
    print("No users found. Create first admin user.")
    while True:
        username = input("Create username: ").strip()
        password = getpass("Create password: ").strip()
        confirm_pass = getpass("Confirm password: ").strip()
        if not username or not password:
            print("Username and password cannot be empty.")
            continue
        if password != confirm_pass:
            print("Passwords do not match.")
            continue
        password_hash = ph.hash(password)
        user = {
            "username": username,
            "password": password_hash,
            "is_admin": True
        }
        collection.insert_one(user)
        print("First admin user created.")
        break

def login_user(
    client,
    database_name: str,
    username: str,
    password: str
) -> dict | None:
    collection = get_collection(client, database_name, "users")
    if not username or not password:
        return None
    db_user = collection.find_one({"username": username})
    if db_user is None:
        return None
    password_hash = db_user.get("password")
    if not password_hash:
        return None
    ph = PasswordHasher()
    try:
        if ph.verify(password_hash, password):
            return db_user

    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return None

    return None