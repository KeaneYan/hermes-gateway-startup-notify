---
name: gateway-startup-notify
description: Hermes gateway startup / restart notification hook for WeChat (Weixin) via the iLink Bot API and gateway:startup event
version: 1.2.1
author: Hermes Community
license: MIT
metadata:
  hermes:
    tags: [gateway, startup, restart, hook, notification, gateway-startup, weixin, wechat, ilink]
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

This skill is for users who want a **"gateway is alive again"** message after:
- machine reboot
- `systemctl --user restart hermes-gateway`
- crash recovery
- deploy / pull / restart workflows

It uses the **iLink Bot API** and Hermes' **`gateway:startup` hook event**.

## What this skill gives you

This skill now includes reusable files:
- `templates/HOOK.yaml`
- `templates/handler.py`
- `references/api-notes.md`

Use those instead of rewriting the handler from scratch.

## Prerequisites

You need:
1. a working Hermes gateway setup
2. a reachable iLink / WeChat bot endpoint
3. these env vars configured in your Hermes `.env` or service environment:
   - `WEIXIN_BASE_URL`
   - `WEIXIN_TOKEN`
   - `WEIXIN_NOTIFY_TARGET`

## Install Layout

Create a hook directory:

```bash
mkdir -p ~/.hermes/hooks/gateway-notify
```

Then copy the provided templates:

```bash
cp <skill-dir>/templates/HOOK.yaml ~/.hermes/hooks/gateway-notify/HOOK.yaml
cp <skill-dir>/templates/handler.py ~/.hermes/hooks/gateway-notify/handler.py
chmod +x ~/.hermes/hooks/gateway-notify/handler.py
```

If you are reading this through Hermes skill loading, open the linked template files and copy them into place.

## Hook Config

Use this `HOOK.yaml`:

```yaml
event: gateway:startup
handler: handler.py
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `WEIXIN_BASE_URL` | iLink server base URL | `https://your-ilink-server.example.com` |
| `WEIXIN_TOKEN` | API auth token | `Bearer` token value |
| `WEIXIN_NOTIFY_TARGET` | Target WeChat OpenID | `openid@im.wechat` |

## Required iLink Headers

The iLink API is picky. These headers must be correct:

| Header | Value | Notes |
|--------|-------|-------|
| `iLink-App-ClientVersion` | `131330` | Computed as `(2<<16) | (2<<8) | 0` |
| `Authorization` | `Bearer <token>` | From env var |
| `X-WECHAT-UIN` | random base64-ish string | Must exist |
| `Content-Length` | exact UTF-8 byte length | Must match the encoded body |
| `channel_version` | `2.2.0` | Must match exactly |

## Required JSON Fields

| Field | Type | Value | Note |
|-------|------|-------|------|
| `message_type` | int | `2` | not string |
| `message_state` | int | `2` | not string |
| `item_list[].type` | int | `1` | not string |
| `channel_version` | string | `"2.2.0"` | exact value |
| `to_contact` | string | target OpenID | from env |
| `item_list[].content` | string | notification text | UTF-8 okay |

## Message Behavior

A good startup message usually includes:
- gateway instance name / hostname
- startup timestamp
- connected platforms count or names
- maybe process ID or environment label (`prod` / `home` / `vps`)

Example:

```text
Hermes gateway started successfully
Host: vps-01
Platforms: weixin, feishu
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

If the hook works, the target WeChat account should receive the startup notification.

### 3. Check logs

Hook logs usually land in **`agent.log`**, not `gateway.log`.

Look for:
- hook discovery / execution lines
- HTTP response body from iLink
- failures like `{"ret": -1}`

## Debugging Checklist

If it does not work, check these in order:

1. **Did the hook file get discovered?**
   - wrong path or bad `HOOK.yaml` means it never runs

2. **Did the handler execute?**
   - check `agent.log`

3. **Did the request return HTTP 200 but still fail?**
   - iLink often returns HTTP 200 with `{"ret": -1}`
   - that still means failure

4. **Did you send ints as strings?**
   - this is a common silent-failure cause

5. **Did `Content-Length` match UTF-8 byte count?**
   - especially important if the message contains Chinese text

6. **Did Hermes / Weixin constants change upstream?**
   - if `weixin.py` changes `CHANNEL_VERSION` or `ILINK_APP_CLIENT_VERSION`, update the handler accordingly

## Common Pitfalls

- iLink accepts the request but returns `ret = -1`
- integer fields serialized as strings
- missing `X-WECHAT-UIN`
- wrong `channel_version`
- stale token / wrong target OpenID
- editing the hook but forgetting to restart the gateway

## How It Works

1. Hermes gateway finishes startup
2. Hermes emits the `gateway:startup` hook event
3. Hook loader discovers `~/.hermes/hooks/gateway-notify/HOOK.yaml`
4. `handler.py` runs
5. Handler posts a text message to the iLink Bot API
6. WeChat receives the notification

## References

See linked files for copy-pasteable assets and API notes:
- `templates/HOOK.yaml`
- `templates/handler.py`
- `references/api-notes.md`
