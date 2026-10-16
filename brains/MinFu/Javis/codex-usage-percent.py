"""Read current Codex subscription rate-limit percentages via the local app-server.

This is a read-only account query. It does not start an inference turn or print auth data.
"""

import json
import queue
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone, timedelta


def main() -> int:
    executable = shutil.which("codex.cmd") or shutil.which("codex")
    if not executable:
        print("Codex CLI unavailable", file=sys.stderr)
        return 1

    command = ["cmd.exe", "/c", executable, "app-server", "--stdio"] if executable.lower().endswith(".cmd") else [executable, "app-server", "--stdio"]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    messages = queue.Queue()

    def read_stdout() -> None:
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except json.JSONDecodeError:
                pass

    threading.Thread(target=read_stdout, daemon=True).start()

    def send(message: dict) -> None:
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    def response(request_id: int) -> dict:
        while True:
            message = messages.get(timeout=12)
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(message["error"].get("message", "unknown RPC error"))
                return message.get("result") or {}

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "javis_usage", "title": "Javis Usage", "version": "1.0.0"}, "capabilities": {}}})
        response(1)
        send({"jsonrpc": "2.0", "method": "initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "account/rateLimits/read", "params": {}})
        limits = response(2).get("rateLimits") or {}
        if limits.get("limitId") != "codex":
            raise RuntimeError("Codex rate limits unavailable")

        vietnam = timezone(timedelta(hours=7))
        for label, field, expected_minutes in (("5h", "primary", 300), ("week", "secondary", 10080)):
            window = limits.get(field) or {}
            if window.get("windowDurationMins") != expected_minutes or not isinstance(window.get("usedPercent"), (int, float)):
                raise RuntimeError(f"{label} rate-limit window unavailable")
            remaining = max(0, min(100, 100 - window["usedPercent"]))
            reset = datetime.fromtimestamp(window["resetsAt"], vietnam).strftime("%H:%M %d/%m") if window.get("resetsAt") else "unknown"
            print(f"{label}_remaining_percent={remaining:g}; reset_vn={reset}")
        return 0
    except (RuntimeError, queue.Empty, KeyError, OSError, ValueError) as exc:
        print(f"Codex usage unavailable: {exc}", file=sys.stderr)
        return 1
    finally:
        process.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
