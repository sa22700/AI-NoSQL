# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
from core.ErrorLog import log_error

def show_page(page: ft.Page, state, api, go) -> None:
    page.clean()
    collections_txt = ft.Text("Collections: -")
    status_txt = ft.Text("")

    async def logout_click(e) -> None:
        state.database_name = ""
        state.collection_name = ""
        state.username = ""
        state.password = ""
        go("login")

    async def exit_click(e) -> None:
        await page.window.destroy()

    async def load_collections_click(e) -> None:
        payload = {
            "database_name": state.database_name,
            "username": state.username,
            "password": state.password,
        }
        try:
            response = await api.list_collections(payload)
            if response.status_code != 200:
                collections_txt.value = f"Collections load failed: {response.text}"
                page.update()
                return
            data = response.json()
            collections = data.get("collections", [])
            if collections:
                collections_txt.value = "Collections: " + ", ".join(collections)
            else:
                collections_txt.value = "Collections: none"
            page.update()

        except Exception as ex:
            log_error(f"Collections load failed: {ex}")
            collections_txt.value = f"Collections load failed: {ex}"
            page.update()

    def nav(route: str):
        async def _handler(e) -> None:
            go(route)
        return _handler

    page.add(
        ft.Column(
            [
                ft.Text(f"Logged in as: {state.username}"),
                ft.Text(f"Database: {state.database_name}"),
                ft.Text(f"Collection: {state.collection_name or '-'}"),
                ft.Row(
                    [
                        collections_txt,
                        ft.Button("Refresh collections", on_click=load_collections_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.Button("Query", on_click=nav("query")),
                        ft.Button("Add document", on_click=nav("database")),
                        ft.Button("Update document", on_click=nav("update-document")),
                        ft.Button("Drop collection", on_click=nav("drop-collection")),
                        ft.Button("Add user", on_click=nav("register")),
                        ft.Button("Delete user", on_click=nav("delete-user")),
                        ft.Button("Update user", on_click=nav("update-user")),
                        ft.Button("Logout", on_click=logout_click),
                        ft.Button("Exit", on_click=exit_click),
                    ],
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()