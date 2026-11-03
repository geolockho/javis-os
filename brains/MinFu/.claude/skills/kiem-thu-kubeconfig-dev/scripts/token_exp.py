"""In thời hạn (exp) của token trong kubeconfig dev, KHÔNG in token.

Cách dùng: python token_exp.py <đường dẫn kubeconfig>
Cần kubectl trong PATH (dùng kubectl để đọc YAML, khỏi cần thư viện yaml).
"""
import base64
import json
import subprocess
import sys
from datetime import datetime, timezone


def main() -> int:
    if len(sys.argv) != 2:
        print("Cách dùng: python token_exp.py <kubeconfig>")
        return 2
    kc = sys.argv[1]
    out = subprocess.run(
        ["kubectl", "config", "view", "--kubeconfig", kc, "--raw",
         "-o", "jsonpath={.users[0].user.token}"],
        capture_output=True, text=True,
    )
    token = out.stdout.strip()
    if out.returncode != 0 or token.count(".") != 2:
        print("Không đọc được token dạng JWT trong kubeconfig.")
        return 1
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    exp = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    iat = datetime.fromtimestamp(claims.get("iat", claims["exp"]), tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    sub = claims.get("sub", "")
    print(f"sub: {sub}")
    print(f"iat: {iat.isoformat()}")
    print(f"exp: {exp.isoformat()}")
    print(f"thoi_han_cap_gio: {(exp - iat).total_seconds() / 3600:.1f}")
    print(f"con_lai_gio: {(exp - now).total_seconds() / 3600:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
