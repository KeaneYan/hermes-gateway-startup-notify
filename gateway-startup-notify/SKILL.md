---
name: gateway-startup-notify
description: Gateway startup hook that sends notification via WeChat (iLink Bot API) when gateway restarts
version: 1.1.0
author: Hermes Community
license: MIT
metadata:
  hermes:
    tags: [gateway, hook, notification, weixin, wechat, ilink]
    category: devops
---

# Gateway Startup Notify Hook

Sends a WeChat notification automatically when the Hermes gateway finishes starting up. Uses the iLink Bot API.

## Setup

### 1. Create Hook Directory

```bash
mkdir -p ~/.hermes/hooks/gateway-notify
```

### 2. Create HOOK.yaml

```yaml
# ~/.hermes/hooks/gateway-notify/HOOK.yaml
event: gateway:startup
handler: handler.py
```

### 3. Create handler.py

The handler script should:

1. Read connection config from environment variables: `WEIXIN_BASE_URL`, `WEIXIN_TOKEN`, `WEIXIN_NOTIFY_TARGET`
2. Build a JSON payload with the notification message
3. POST to the iLink Bot API at `{base_url}/api/v2/chat/contact`
4. Parse the response and check `ret` field (0 = success, -1 = failure)

Configure these variables in your Hermes `.env` file. The `WEIXIN_NOTIFY_TARGET` should be the WeChat OpenID of the notification recipient.

### 4. Required iLink HTTP Headers

The API requires these exact headers or it silently fails:

| Header | Value | Notes |
|--------|-------|-------|
| `iLink-App-ClientVersion` | `"131330"` | Computed as `(2<<16)\|(2<<8)\|0` |
| `Authorization` | `Bearer <token>` | From env var |
| `X-WECHAT-UIN` | Random base64 string | Must be present, value doesn't matter |
| `Content-Length` | Exact body byte length | Must match |
| `channel_version` | `"2.2.0"` | Must match exactly |

### 5. Required JSON Body Fields

| Field | Type | Value | Note |
|-------|------|-------|------|
| `message_type` | **int** | `2` | NOT string `"bot"` |
| `message_state` | **int** | `2` | NOT string `"finish"` |
| `item_list[].type` | **int** | `1` | NOT string `"text"` |
| `channel_version` | string | `"2.2.0"` | NOT `"1.0.0"` |
| `to_contact` | string | Target OpenID | From env var |
| `item_list[].content` | string | Your message | UTF-8 supported |

## iLink API Pitfalls

The iLink API is extremely strict about request format. Wrong values cause **silent failures** — HTTP 200 with `{"ret": -1}`:

- Integer fields must be actual integers, not strings
- `iLink-App-ClientVersion` must be the numeric encoding, not a version string
- `X-WECHAT-UIN` header must exist even though the value is arbitrary
- `Content-Length` must be exact byte count of UTF-8 encoded body

## Debugging

- Hook logs appear in **`agent.log`** (not `gateway.log`) — the gateway log filter only accepts `gateway.*` logger prefixes
- **Always check response body** — HTTP 200 + `{"ret":-1}` means failure
- If Hermes updates weixin.py constants, update `CHANNEL_VERSION` and `ILINK_APP_CLIENT_VERSION` accordingly

## How It Works

1. Gateway emits `gateway:startup` event after all platforms connect
2. Hook system discovers and loads hooks from `~/.hermes/hooks/`
3. Handler receives connected platform list and sends notification via iLink API

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `WEIXIN_BASE_URL` | iLink server URL | `https://your-ilink-server.example.com` |
| `WEIXIN_TOKEN` | API authentication token | (set in .env) |
| `WEIXIN_NOTIFY_TARGET` | Recipient WeChat OpenID | `openid@im.wechat` |
