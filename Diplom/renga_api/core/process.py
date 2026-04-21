"""Helpers for inspecting and controlling local Renga processes on Windows."""

from __future__ import annotations

import json
import subprocess
from typing import Any

from .app import reset_connection

_POWERSHELL = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
_RENGA_PROCESS_NAME = "Renga"


def _run_powershell(command: str) -> str:
    """Run a PowerShell command and return its stdout."""
    completed = subprocess.run(
        [_POWERSHELL, "-NoProfile", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        raise RuntimeError(stderr or f"PowerShell command failed: {command}")
    return completed.stdout.strip()


def list_renga_processes() -> list[dict[str, Any]]:
    """Return metadata for running Renga processes."""
    command = _build_list_processes_command()
    raw = _run_powershell(command)
    return _parse_process_items(raw)


def stop_renga_process(pid: int, *, force: bool = True) -> dict[str, Any]:
    """Stop a specific Renga process by PID."""
    processes = list_renga_processes()
    target = next((item for item in processes if item["pid"] == pid), None)
    if target is None:
        raise RuntimeError(f"Renga process with pid={pid} was not found.")

    command = f"Stop-Process -Id {int(pid)}{' -Force' if force else ''}"
    _run_powershell(command)
    reset_connection()
    return {"pid": int(pid), "stopped": True, "success": True}


def stop_all_renga_processes(*, force: bool = True) -> dict[str, Any]:
    """Stop all running Renga processes."""
    processes = list_renga_processes()
    if not processes:
        reset_connection()
        return {"pids": [], "stopped_count": 0, "success": True}

    pids = [int(item["pid"]) for item in processes]
    joined_pids = ",".join(str(pid) for pid in pids)
    command = f"Stop-Process -Id {joined_pids}{' -Force' if force else ''}"
    _run_powershell(command)
    reset_connection()
    return {"pids": pids, "stopped_count": len(pids), "success": True}


def _build_list_processes_command() -> str:
    return (
        "$ErrorActionPreference = 'Stop'; "
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        f"$items = @(Get-Process -Name '{_RENGA_PROCESS_NAME}' -ErrorAction SilentlyContinue "
        "| Sort-Object Id "
        "| Select-Object "
        "Id, ProcessName, Path, MainWindowTitle, MainWindowHandle, Responding, "
        "@{Name='HasMainWindow';Expression={ [bool]$_.MainWindowHandle }}, "
        "@{Name='StartTime';Expression={ try { if ($_.StartTime) { $_.StartTime.ToString('o') } else { $null } } catch { $null } }}); "
        "if ($items.Count -gt 0) { $items | ConvertTo-Json -Depth 3 -Compress }"
    )


def _parse_process_items(raw: str) -> list[dict[str, Any]]:
    raw = raw.strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        snippet = raw[:200]
        raise RuntimeError(f"Failed to parse PowerShell process output as JSON: {snippet}") from error

    if isinstance(data, dict):
        data = [data]

    return [
        {
            "pid": item.get("Id"),
            "process_name": item.get("ProcessName"),
            "path": item.get("Path"),
            "main_window_title": item.get("MainWindowTitle"),
            "main_window_handle": item.get("MainWindowHandle"),
            "has_main_window": bool(item.get("HasMainWindow")),
            "responding": item.get("Responding"),
            "start_time": item.get("StartTime"),
        }
        for item in data
    ]
