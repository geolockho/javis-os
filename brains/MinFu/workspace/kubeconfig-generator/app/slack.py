"""Gửi thông báo Slack qua incoming webhook. Lỗi chỉ log cảnh báo, không làm hỏng request."""
from __future__ import annotations

import json
import logging
import threading
import urllib.request

log = logging.getLogger(__name__)


def _post(url: str, payload: dict, timeout: float) -> None:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - URL lấy từ cấu hình admin
            if resp.status >= 300:
                log.warning("Slack trả mã %s", resp.status)
    except Exception as exc:  # noqa: BLE001
        # Không in URL webhook (là bí mật)
        log.warning("Gửi Slack lỗi: %s", type(exc).__name__)


def notify(url: str, text: str, timeout: float = 5.0, background: bool = True) -> None:
    if not url:
        return
    payload = {"text": text}
    if background:
        threading.Thread(target=_post, args=(url, payload, timeout), daemon=True).start()
    else:
        _post(url, payload, timeout)
