"""Read-only hardware inventory. No network calls or mutation."""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def read_linux_meminfo(path: str = "/proc/meminfo") -> int | None:
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def read_cpu_model(path: str = "/proc/cpuinfo") -> str | None:
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def collect_inventory() -> dict:
    disk = shutil.disk_usage("/")
    return {
        "system": platform.system(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "cpu_model": read_cpu_model(),
        "logical_cpus": os.cpu_count(),
        "ram_total_bytes": read_linux_meminfo(),
        "disk_root_total_bytes": disk.total,
        "disk_root_free_bytes": disk.free,
        "model_backend_configured": False,  # inventory is independent of runtime settings
    }
