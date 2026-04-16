#!/usr/bin/env python3
"""Gateway startup hook: send a WeChat notification through iLink."""

import base64
import json
import os
import random
import socket
import string
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

CHANNEL_VERSION = "2.2.0"
ILINK_APP_CLIENT_VERSION = str((2 << 16) | (2 << 8) | 0)  # 131330


def _rand_uin(length: int = 16) -> str:
    raw = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    return base64.b64encode(raw.encode()).decode()


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _build_message(event: dict) -> str:
    host = socket.gethostname()
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    platforms = event.get("platforms") or []
    if isinstance(platforms, list):
        platform_text = ", ".join(str(p) for p in platforms) if platforms else "(none)"
    else:
        platform_text = str(platforms)

    return (
        "Hermes gateway started successfully\n"
        f"Host: {host}\n"
        f"Platforms: {platform_text}\n"
        f"Time: {now}"
    )


def main() -> int:
    try:
        base_url = _require_env("WEIXIN_BASE_URL").rstrip("/")
        token = _require_env("WEIXIN_TOKEN")
        target = _require_env("WEIXIN_NOTIFY_TARGET")

        event = json.load(sys.stdin) if not sys.stdin.isatty() else {}
        message = _build_message(event)

        body = {
            "message_type": 2,
            "message_state": 2,
            "channel_version": CHANNEL_VERSION,
            "to_contact": target,
            "item_list": [
                {
                    "type": 1,
                    "content": message,
                }
            ],
        }
        data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(data)),
            "iLink-App-ClientVersion": ILINK_APP_CLIENT_VERSION,
            "X-WECHAT-UIN": _rand_uin(),
            "channel_version": CHANNEL_VERSION,
        }

        req = urllib.request.Request(
            f"{base_url}/api/v2/chat/contact",
            data=data,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            print(f"iLink status={resp.status}")
            print(raw)
            payload = json.loads(raw)

        if payload.get("ret") != 0:
            raise RuntimeError(f"iLink returned failure payload: {payload}")
        return 0

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTPError: status={exc.code} body={body}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"gateway-startup-notify hook failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
