# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
import json
from core.ErrorLog import log_error

def show_query(page: ft.Page, state, api, go) -> None:
    page.clean()
    collection_tf = ft.TextField(
        label="Collection name",
        value=state.collection_name,
        width=400,
    )
    question_tf = ft.TextField(
        label="Question",
        multiline=True,
        min_lines=3,
        max_lines=6,
        width=600,
    )
    status_txt = ft.Text("")
    result_tf = ft.TextField(
        label="Result",
        multiline=True,
        read_only=True,
        width=700,
        min_lines=10,
    )

    async def run_click(e) -> None:
        collection_name = (collection_tf.value or "").strip()
        question = (question_tf.value or "").strip()
        if not collection_name:
            status_txt.value = "Collection name is missing"
            page.update()
            return
        if not question:
            status_txt.value = "Question is missing"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "collection_name": collection_name,
            "username": state.username,
            "password": state.password,
            "query": question,
        }
        status_txt.value = "Running..."
        page.update()
        try:
            response = await api.ai_nosql(payload)
            if response.status_code != 200:
                try:
                    status_txt.value = f"Error {response.status_code}: {response.json().get('detail')}"

                except Exception:
                    status_txt.value = f"Error {response.status_code}: {response.text}"

                page.update()
                return
            data = response.json()
            state.collection_name = collection_name
            status_txt.value = "OK"
            result_tf.value = json.dumps(data, indent=2, ensure_ascii=False)
            page.update()

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def logout_click(e) -> None:
        state.database_name = ""
        state.collection_name = ""
        state.username = ""
        state.password = ""
        go("login")

    async def exit_click(e) -> None:
        await page.window.destroy()

    async def back_click(e) -> None:
        go("main menu")

    page.add(
        ft.Column(
            [
                ft.Text(f"Logged in as: {state.username}"),
                ft.Text(f"Database: {state.database_name}"),
                collection_tf,
                question_tf,
                ft.Row(
                    [
                        ft.Button("Run", on_click=run_click),
                        ft.Button("Back", on_click=back_click),
                        ft.Button("Logout", on_click=logout_click),
                        ft.Button("Exit", on_click=exit_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
                result_tf,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()