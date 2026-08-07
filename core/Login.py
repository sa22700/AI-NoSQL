# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from getpass import getpass
from argon2 import PasswordHasher
from pymongo.errors import PyMongoError
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from core.Database import get_collection

def ensure_first_user(
    client,
    database_name: str,
    username: str | None = None,
    password: str | None = None,
    confirm_password: str | None = None,
    interactive: bool = True,
    print_output: bool = True
) -> dict:
    collection = get_collection(client, database_name, "users")
    try:
        if collection.count_documents({}) > 0:
            return {
                "ok": True,
                "created": False,
                "username": None,
                "error": None,
            }
        ph = PasswordHasher()
        if print_output:
            print("No users found. Create first admin user.")
        if interactive:
            while True:
                username = input("Create username: ").strip()
                password = getpass("Create password: ").strip()
                confirm_password = getpass("Confirm password: ").strip()
                if not username or not password:
                    if print_output:
                        print("Username and password cannot be empty.")
                    continue
                if password != confirm_password:
                    if print_output:
                        print("Passwords do not match.")
                    continue
                break
        else:
            username = (username or "").strip()
            password = (password or "").strip()
            confirm_password = (confirm_password or "").strip()
            if not username or not password:
                return {
                    "ok": False,
                    "created": False,
                    "username": None,
                    "error": "Username and password cannot be empty.",
                }
            if password != confirm_password:
                return {
                    "ok": False,
                    "created": False,
                    "username": None,
                    "error": "Passwords do not match.",
                }
        user = {
            "username": username,
            "password": ph.hash(password),
            "is_admin": True,
        }
        collection.insert_one(user)
        if print_output:
            print("First admin user created.")
        return {
            "ok": True,
            "created": True,
            "username": username,
            "error": None,
        }

    except PyMongoError as error:
        return {
            "ok": False,
            "created": False,
            "username": None,
            "error": str(error),
        }

    except EOFError as error:
        return {
            "ok": False,
            "created": False,
            "username": None,
            "error": str(error),
        }

    except KeyboardInterrupt as error:
        return {
            "ok": False,
            "created": False,
            "username": None,
            "error": str(error),
        }

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

def require_admin(
    client,
    database_name: str,
    username: str,
    password: str
) -> dict | None:
    user = login_user(
        client=client,
        database_name=database_name,
        username=username,
        password=password,
    )
    if user is None:
        return None
    if not user.get("is_admin"):
        return None
    return user