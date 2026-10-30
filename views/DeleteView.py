# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
from core.ErrorLog import log_error

def show_delete(page: ft.Page, state, api, go) -> None:
    page.clean()
    username_del_tf = ft.TextField(label="Username to delete", width=400)
    confirm_cb = ft.Checkbox(label="I confirm delete", value=False)
    status_txt = ft.Text("")

    async def do_delete_click(e) -> None:
        user = (username_del_tf.value or "").strip()
        if not user:
            status_txt.value = "Username missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm delete first"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "username": state.username,
            "password": state.password,
            "username_to_delete": user,
            "confirm": bool(confirm_cb.value),
        }
        status_txt.value = "Deleting..."
        page.update()
        try:
            response = await api.delete_user(payload)
            if not (200 <= response.status_code < 300):
                try:
                    status_txt.value = f"Delete failed: {response.json().get('detail')}"

                except Exception:
                    log_error(f"Delete failed: {response.text}")
                    status_txt.value = f"Delete failed: {response.text}"

                page.update()
                return
            data = response.json()
            status_txt.value = f"OK: deleted {data.get('deleted')}"
            confirm_cb.value = False
            page.update()

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def back_click(e) -> None:
        go("main menu")

    page.add(
        ft.Column(
            [
                ft.Text(f"Admin: {state.username}"),
                ft.Text(f"Database: {state.database_name}"),
                username_del_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Delete", on_click=do_delete_click),
                        ft.Button("Back", on_click=back_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()