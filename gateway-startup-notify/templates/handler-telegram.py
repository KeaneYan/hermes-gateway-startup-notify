#!/usr/bin/env python3
"""Gateway startup hook: send a Telegram notification when Hermes gateway starts."""

import json
import os
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


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
        "✅ Hermes gateway started successfully\n"
        f"Host: {host}\n"
        f"Platforms: {platform_text}\n"
        f"Time: {now}"
    )


def main() -> int:
    try:
        token = _require_env("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_HOME_CHANNEL", "").strip()
        if not chat_id:
            chat_id = _require_env("TELEGRAM_ALLOWED_USERS").split(",")[0].strip()

        # Optional proxy (for environments behind a firewall)
        proxy_url = os.environ.get("TELEGRAM_PROXY", "").strip()

        event = json.load(sys.stdin) if not sys.stdin.isatty() else {}
        message = _build_message(event)

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = {
            "chat_id": chat_id,
            "text": message,
        }
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        # Use proxy if configured
        if proxy_url:
            proxy_handler = urllib.request.ProxyHandler({"https": proxy_url, "http": proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()

        with opener.open(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            print(f"Telegram status={resp.status}")
            payload = json.loads(raw)

        if not payload.get("ok"):
            raise RuntimeError(f"Telegram API returned failure: {payload}")
        print("Notification sent successfully")
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
