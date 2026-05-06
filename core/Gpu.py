# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import subprocess
import shutil

def cuda_available() -> float:
    try:
        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            return 0
        result = subprocess.run(
            [nvidia_smi, "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        values: list[int] = []
        for line in result.stdout.splitlines():
            if not line:
                continue
            try:
                values.append(int(line))

            except ValueError:
                continue

        if not values:
            return 0
        return max(values) / 1024

    except Exception as e:
        print(f"VRAM-check failed: {e}")
        log_error(f"VRAM-check failed: {e}")
        return 0.0

def estimate_n_gpu_layers(vram_gb) -> int:
    if vram_gb <= 0:
        return 0
    elif vram_gb <= 4:
        return 5
    elif vram_gb <= 6:
        return 10
    elif vram_gb <= 8:
        return 15
    elif vram_gb <= 10:
        return 20
    elif vram_gb <= 12:
        return 30
    return 35