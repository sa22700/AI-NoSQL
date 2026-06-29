# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import traceback
import os

def log_error(error_message) -> None:
    with open(os.getenv("ERROR_LOGS"), "a", encoding="utf-8") as log:
        log.write(f"Error: {error_message}\n")
        log.write(traceback.format_exc())
        log.write("\n" + "=" * 40 + "\n")