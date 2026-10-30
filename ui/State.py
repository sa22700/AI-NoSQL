# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

@dataclass
class AppState:
    database_name: str = ""
    collection_name: str = ""
    username: str = ""
    password: str = ""