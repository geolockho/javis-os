"""Bộ lọc log: che token SA (JWT), token link tải và chuỗi bí mật trước khi ghi ra.

Đây là lớp phòng thủ thứ hai. Lớp thứ nhất là code không bao giờ đưa token vào log.
"""
from __future__ import annotations

import logging
import re

# JWT: 3 đoạn base64url, đoạn đầu luôn bắt đầu bằng eyJ ('{"' sau khi base64)
_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}")
# token=..., "token": "...", Authorization: Bearer ...
_KV_RE = re.compile(r"(?i)(token|secret|password|authorization)(\"?\s*[:=]\s*\"?)(bearer\s+)?[^\s\"',&}]+")
# Token link tải là token_urlsafe(32) = 43 ký tự base64url
_LINK_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{43}(?![A-Za-z0-9_-])")
_SLACK_RE = re.compile(r"https://hooks\.slack\.com/[^\s\"']+")

REDACTED = "[REDACTED]"


def redact(text: str) -> str:
    if not text:
        return text
    text = _JWT_RE.sub(REDACTED, text)
    text = _SLACK_RE.sub(REDACTED, text)
    text = _KV_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}{REDACTED}", text)
    text = _LINK_TOKEN_RE.sub(REDACTED, text)
    return text


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:  # noqa: BLE001 - không để lỗi format làm mất log
            msg = str(record.msg)
        record.msg = redact(msg)
        record.args = None
        if record.exc_info and not record.exc_text:
            record.exc_text = logging.Formatter().formatException(record.exc_info)
        if record.exc_text:
            record.exc_text = redact(record.exc_text)
        return True


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.addFilter(RedactFilter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    # Access log của uvicorn bị tắt ở main (app tự ghi access log đã lọc).
    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers[:] = []
        lg.propagate = True
    # Client kubernetes có thể in header ở mức DEBUG
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("kubernetes").setLevel(logging.WARNING)
