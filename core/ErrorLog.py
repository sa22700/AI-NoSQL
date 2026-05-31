# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import traceback

LOG_FILE = os.getenv("ERROR_LOGS")

def log_error(error_message) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Error: {error_message}\n")
        log.write(traceback.format_exc())
        log.write("\n" + "=" * 40 + "\n")