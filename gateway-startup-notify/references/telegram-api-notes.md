# Telegram Bot API Notes

Tips for the Telegram gateway startup notification handler.

## Endpoint

The handler posts to the Telegram Bot API:

```text
https://api.telegram.org/bot<TOKEN>/sendMessage
```

## Env Vars

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes |
| `TELEGRAM_HOME_CHANNEL` | Target chat ID | No (falls back to first `TELEGRAM_ALLOWED_USERS`) |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated allowed user IDs | Fallback if `TELEGRAM_HOME_CHANNEL` is unset |
| `TELEGRAM_PROXY` | HTTPS proxy URL | No |

Hermes already stores these in `.env` for the Telegram platform, so no extra
configuration is usually needed.

## Success Pattern

Telegram returns HTTP 200 with:

```json
{"ok": true, "result": {...}}
```

Check `payload.get("ok")` — if false, the request failed even with HTTP 200.

## Proxy Support

If `TELEGRAM_PROXY` is set (e.g. `http://127.0.0.1:7897`), the handler routes
through that proxy. This is useful in regions where Telegram is blocked.

Hermes also sets `HTTPS_PROXY` globally in `.env` for some setups. The handler
does not read that automatically — set `TELEGRAM_PROXY` explicitly if needed.

## No Special Headers

Unlike the iLink / WeChat API, the Telegram Bot API is straightforward:

- Standard `Content-Type: application/json`
- No custom version headers
- No random UIN fields
- No strict `Content-Length` requirements

## Message Format

A plain text message is sent. The default format:

```text
✅ Hermes gateway started successfully
Host: my-server
Platforms: telegram, discord
Time: 2026-04-17 15:30:00 CST
```

You can extend `handler-telegram.py` to use Markdown or HTML formatting by
adding `"parse_mode": "Markdown"` or `"parse_mode": "HTML"` to the request body.
