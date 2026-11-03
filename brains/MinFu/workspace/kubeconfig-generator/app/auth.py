"""Danh tính người dùng lấy từ header do oauth2-proxy (sidecar) gắn vào.

App chỉ nghe 127.0.0.1 trong pod, nên mọi request tới app đều đã đi qua oauth2-proxy.
oauth2-proxy ghi đè header X-Forwarded-Email, client không tự đặt được.
Quyền xin namespace KHÔNG dựa vào group GitLab: chỉ cần email đăng nhập, admin duyệt từng request.
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request

from .config import Settings


@dataclass(frozen=True)
class Identity:
    email: str
    is_admin: bool = False


def identity_from_request(request: Request, settings: Settings) -> Identity:
    email = (request.headers.get(settings.email_header) or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập SSO")
    return Identity(email=email, is_admin=settings.is_admin(email))


def require_admin(identity: Identity) -> Identity:
    if not identity.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ admin")
    return identity


def client_ip(request: Request, settings: Settings) -> str:
    ip = (request.headers.get(settings.client_ip_header) or "").strip()
    if ip:
        # X-Forwarded-For có thể là chuỗi; lấy phần tử đầu do ingress đặt
        return ip.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
