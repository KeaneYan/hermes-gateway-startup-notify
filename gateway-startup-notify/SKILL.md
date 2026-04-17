---
name: gateway-startup-notify
description: Hermes gateway startup / restart notification hook for WeChat (Weixin) via iLink, or Telegram via Bot API, on the gateway:startup event
version: 1.3.0
author: Hermes Community
license: MIT
metadata:
  hermes:
    tags: [gateway, startup, restart, hook, notification, gateway-startup, weixin, wechat, ilink, telegram]
    category: devops
---

# Gateway Startup Notify Hook

Send a **Hermes gateway startup notification** automatically when the gateway finishes starting up.

This skill targets common search intents like:
- Hermes gateway
- gateway startup notification
- restart notification
- gateway:startup hook
- WeChat hook
- Weixin hook
- iLink bot API
- Telegram notification
- Telegram bot hook

This skill is for users who want a **"gateway is alive again"** message after:
- machine reboot
- `systemctl --user restart hermes-gateway`
- crash recovery
- deploy / pull / restart workflows

## Supported Channels

| Channel | Handler | API |
|---------|---------|-----|
| WeChat / Weixin | `handler.py` | iLink Bot API |
| Telegram | `handler-telegram.py` | Telegram Bot API |

## What this skill gives you

This skill includes reusable files:
- `templates/HOOK.yaml` — shared hook config
- `templates/handler.py` — WeChat / iLink handler
- `templates/handler-telegram.py` — Telegram handler
- `references/api-notes.md` — iLink API notes
- `references/telegram-api-notes.md` — Telegram API notes

Use those instead of rewriting the handler from scratch.

---

## Option A: WeChat / Weixin (iLink)

### Prerequisites

1. a working Hermes gateway setup
2. a reachable iLink / WeChat bot endpoint
3. these env vars configured in your Hermes `.env` or service environment:
   - `WEIXIN_BASE_URL`
   - `WEIXIN_TOKEN`
   - `WEIXIN_NOTIFY_TARGET`

### Install

```bash
mkdir -p ~/.hermes/hooks/gateway-notify
cp <skill-dir>/templates/HOOK.yaml ~/.hermes/hooks/gateway-notify/HOOK.yaml
cp <skill-dir>/templates/handler.py ~/.hermes/hooks/gateway-notify/handler.py
chmod +x ~/.hermes/hooks/gateway-notify/handler.py
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `WEIXIN_BASE_URL` | iLink server base URL | `https://your-ilink-server.example.com` |
| `WEIXIN_TOKEN` | API auth token | `Bearer` token value |
| `WEIXIN_NOTIFY_TARGET` | Target WeChat OpenID | `openid@im.wechat` |

### Required iLink Headers

| Header | Value | Notes |
|--------|-------|-------|
| `iLink-App-ClientVersion` | `131330` | Computed as `(2<<16) | (2<<8) | 0` |
| `Authorization` | `Bearer <token>` | From env var |
| `X-WECHAT-UIN` | random base64-ish string | Must exist |
| `Content-Length` | exact UTF-8 byte length | Must match the encoded body |
| `channel_version` | `2.2.0` | Must match exactly |

### Required JSON Fields

| Field | Type | Value | Note |
|-------|------|-------|------|
| `message_type` | int | `2` | not string |
| `message_state` | int | `2` | not string |
| `item_list[].type` | int | `1` | not string |
| `channel_version` | string | `"2.2.0"` | exact value |
| `to_contact` | string | target OpenID | from env |
| `item_list[].content` | string | notification text | UTF-8 okay |

---

## Option B: Telegram

### Prerequisites

1. a working Hermes gateway setup
2. a Telegram bot (created via @BotFather)
3. these env vars already in your Hermes `.env` (same ones Hermes uses for Telegram):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_ALLOWED_USERS` or `TELEGRAM_HOME_CHANNEL`

### Install

```bash
mkdir -p ~/.hermes/hooks/gateway-notify
cp <skill-dir>/templates/HOOK.yaml ~/.hermes/hooks/gateway-notify/HOOK.yaml
cp <skill-dir>/templates/handler-telegram.py ~/.hermes/hooks/gateway-notify/handler.py
chmod +x ~/.hermes/hooks/gateway-notify/handler.py
```

> Note: copy `handler-telegram.py` as `handler.py` so the HOOK.yaml `handler` field works without changes.

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes |
| `TELEGRAM_HOME_CHANNEL` | Target chat ID | No (falls back to first `TELEGRAM_ALLOWED_USERS`) |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated allowed user IDs | Fallback if `TELEGRAM_HOME_CHANNEL` unset |
| `TELEGRAM_PROXY` | HTTPS proxy URL | No |

### Proxy Support

If you are behind a firewall or in a region where Telegram is blocked, set `TELEGRAM_PROXY` in your `.env`:

```
TELEGRAM_PROXY=http://127.0.0.1:7897
```

---

## Shared Config

### Hook Config (HOOK.yaml)

```yaml
event: gateway:startup
handler: handler.py
```

This is the same for both channels. Just pick the right handler file when installing.

### Message Behavior

A good startup message usually includes:
- gateway instance name / hostname
- startup timestamp
- connected platforms count or names
- maybe process ID or environment label (`prod` / `home` / `vps`)

Example:

```text
✅ Hermes gateway started successfully
Host: vps-01
Platforms: telegram, discord
Time: 2026-04-16 14:03:12
```

## Verification

After installing the hook:

### 1. Restart gateway

```bash
systemctl --user restart hermes-gateway
```

Or start it manually if that's how you run Hermes.

### 2. Check whether the message arrived

If the hook works, the target account (WeChat or Telegram) should receive the startup notification.

### 3. Check logs

Hook logs usually land in **`agent.log`**, not `gateway.log`.

Look for:
- hook discovery / execution lines
- HTTP response body
- failures (iLink: `{"ret": -1}`, Telegram: `{"ok": false}`)

## Debugging Checklist

If it does not work, check these in order:

1. **Did the hook file get discovered?**
   - wrong path or bad `HOOK.yaml` means it never runs

2. **Did the handler execute?**
   - check `agent.log`

3. **Did the request return HTTP 200 but still fail?**
   - iLink often returns HTTP 200 with `{"ret": -1}`
   - Telegram returns `{"ok": false}` on failure
   - both still mean failure

4. **WeChat: did you send ints as strings?**
   - this is a common silent-failure cause for iLink

5. **WeChat: did `Content-Length` match UTF-8 byte count?**
   - especially important if the message contains Chinese text

6. **WeChat: did Hermes / Weixin constants change upstream?**
   - if `weixin.py` changes `CHANNEL_VERSION` or `ILINK_APP_CLIENT_VERSION`, update the handler accordingly

7. **Telegram: is the bot token correct?**
   - verify with `curl https://api.telegram.org/bot<TOKEN>/getMe`

8. **Telegram: is the chat ID correct?**
   - the bot must have an active conversation with the user

9. **Did you edit the hook but forget to restart the gateway?**

## Common Pitfalls

### WeChat / iLink
- iLink accepts the request but returns `ret = -1`
- integer fields serialized as strings
- missing `X-WECHAT-UIN`
- wrong `channel_version`
- stale token / wrong target OpenID

### Telegram
- wrong bot token
- chat ID belongs to a user who hasn't started a conversation with the bot
- proxy not configured when Telegram is blocked in the region

## How It Works

1. Hermes gateway finishes startup
2. Hermes emits the `gateway:startup` hook event
3. Hook loader discovers `~/.hermes/hooks/gateway-notify/HOOK.yaml`
4. `handler.py` runs
5. Handler posts a text message (to iLink or Telegram Bot API)
6. The target app receives the notification

## References

See linked files for copy-pasteable assets and API notes:
- `templates/HOOK.yaml`
- `templates/handler.py` (WeChat / iLink)
- `templates/handler-telegram.py` (Telegram)
- `references/api-notes.md` (iLink)
- `references/telegram-api-notes.md` (Telegram)
