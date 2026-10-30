# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
import flet as ft
from ui.State import AppState
from ui.API import ApiClient
from views.LoginView import show_login
from views.QueryView import show_query
from views.RegisterView import show_register
from views.DeleteView import show_delete
from views.DatabaseView import show_database
from views.MenuView import show_page
from views.DropView import show_delete_collection
from views.UpdateView import show_update_document
from views.UsersView import show_update_user

API_BASE = os.getenv('API_BASE')

def main(page: ft.Page) -> None:
    page.title = "AI-NoSQL"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    state = AppState()
    api = ApiClient(API_BASE)

    def go(view: str) -> None:
        routes[view]()

    def route_login() -> None:
        show_login(page, state, api, go)

    def route_query() -> None:
        show_query(page, state, api, go)

    def route_register() -> None:
        show_register(page, state, api, go)

    def route_delete_user() -> None:
        show_delete(page, state, api, go)

    def route_database() -> None:
        show_database(page, state, api, go)

    def route_main() -> None:
        show_page(page, state, api, go)

    def route_drop_collection() -> None:
        show_delete_collection(page, state, api, go)

    def route_update_document() -> None:
        show_update_document(page, state, api, go)

    def route_update_user() -> None:
        show_update_user(page, state, api, go)

    routes = {
        "login": route_login,
        "query": route_query,
        "register": route_register,
        "delete-user": route_delete_user,
        "database": route_database,
        "main menu": route_main,
        "drop-collection": route_drop_collection,
        "update-document": route_update_document,
        "update-user": route_update_user,
    }
    go("login")
ft.run(main)