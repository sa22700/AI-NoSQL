# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import uvicorn
from backend.ModelCall import app
from core.ErrorLog import log_error
from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    try:
        uvicorn.run(
            app,
            host='127.0.0.1',
            port=8000,
            reload=False,
            log_level='info',
        )

    except Exception as ex:
        log_error(f"Error: {ex}")
        print(f"Error: {ex}")


if __name__ == "__main__":
    main()