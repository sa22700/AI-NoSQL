# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
from core.ErrorLog import log_error

def show_update_user(page: ft.Page, state, api, go) -> None:
    page.clean()
    target_tf = ft.TextField(label="Target username", width=400)
    username_tf = ft.TextField(label="New username (optional)", width=400)
    password_tf = ft.TextField(
        label="New password (optional)",
        password=True,
        can_reveal_password=True,
        width=400
    )
    confirm_password_tf = ft.TextField(
        label="Confirm new password",
        password=True,
        can_reveal_password=True,
        width=400
    )
    admin_dropdown = ft.Dropdown(
        label="Admin status",
        width=400,
        value="no_change",
        options=[
            ft.dropdown.Option("no_change", "No change"),
            ft.dropdown.Option("admin", "Admin"),
            ft.dropdown.Option("normal", "Normal user"),
        ],
    )
    confirm_cb = ft.Checkbox(label="I confirm update", value=False)
    status_txt = ft.Text("")

    async def do_update_click(e) -> None:
        target_username = (target_tf.value or "").strip()
        new_username = (username_tf.value or "").strip()
        new_password = password_tf.value or ""
        confirm_password = confirm_password_tf.value or ""
        if not target_username:
            status_txt.value = "Target username missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm update first"
            page.update()
            return
        if confirm_password and not new_password:
            status_txt.value = "New password missing"
            page.update()
            return
        if new_password and new_password != confirm_password:
            status_txt.value = "Passwords do not match"
            page.update()
            return
        if admin_dropdown.value == "admin":
            is_admin = True
        elif admin_dropdown.value == "normal":
            is_admin = False
        else:
            is_admin = None
        new_username = new_username if new_username else None
        new_password = new_password if new_password else None
        confirm_password = confirm_password if new_password else None
        if new_username is None and new_password is None and is_admin is None:
            status_txt.value = "Nothing to update"
            page.update()
            return
        payload = {
            "database_name": state.database_name,
            "username": state.username,
            "password": state.password,
            "username_to_update": target_username,
            "new_username": new_username,
            "new_password": new_password,
            "confirm_password": confirm_password,
            "is_admin": is_admin,
        }
        status_txt.value = "Updating..."
        page.update()
        try:
            loader = await api.update_user(payload)
            data = loader.json() if loader is not None else {}
            if not (200 <= loader.status_code < 300) or data.get("error"):
                detail = data.get("detail") or data.get("error") or getattr(loader, "text", "Unknown error")
                status_txt.value = f"Update failed: {detail}"
                page.update()
                return
            updated = data.get("updated", {})
            updated_username = updated.get("username", target_username)
            status_txt.value = f"OK: updated user {updated_username}"
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
                target_tf,
                ft.Divider(),
                username_tf,
                password_tf,
                confirm_password_tf,
                admin_dropdown,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Update user", on_click=do_update_click),
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