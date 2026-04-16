# iLink / WeChat API Notes

These are the sharp edges that matter for the gateway startup notify hook.

## Endpoint

The handler posts to:

```text
{WEIXIN_BASE_URL}/api/v2/chat/contact
```

## Success / Failure Pattern

Do **not** rely on HTTP status alone.

A failed request may still return HTTP 200 with a body like:

```json
{"ret": -1}
```

Treat `ret != 0` as failure.

## Header Quirks

Required headers that tend to break integrations:

- `Authorization: Bearer <token>`
- `iLink-App-ClientVersion: 131330`
- `X-WECHAT-UIN: <random string>`
- `channel_version: 2.2.0`
- `Content-Length: <exact byte length>`

## Body Quirks

These fields must be typed correctly:

- `message_type`: integer `2`
- `message_state`: integer `2`
- `item_list[0].type`: integer `1`

If you serialize them as strings, the API can fail silently.

## Logging Tip

If the gateway startup hook runs but the message does not arrive, print:

- request URL
- response status
- full response body

That is usually enough to spot a malformed request.

## Drift Risk

If Hermes upstream updates Weixin-related constants in `weixin.py`, re-check:

- `CHANNEL_VERSION`
- `ILINK_APP_CLIENT_VERSION`

This skill intentionally keeps those values visible so they are easy to update.
