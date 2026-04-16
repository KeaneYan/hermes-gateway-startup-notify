# Hermes Gateway Startup Notify

A focused Hermes skill repo for **gateway startup notification**, **restart notification**, and **WeChat / Weixin hook** setup.

This repository currently ships one skill for the Hermes gateway hook system:

## Available Skill

### `gateway-startup-notify`
Send a **Hermes gateway startup notification** through the **WeChat / Weixin iLink Bot API** whenever the gateway finishes starting up.

Useful for:
- confirming a remote Hermes gateway restarted successfully
- getting a startup notification after deploy / reboot
- monitoring always-on Hermes instances
- receiving a **gateway:startup hook** alert in WeChat
- setting up a **restart notification hook** for Hermes

## Install

### Install this repo as a Hermes tap

```bash
hermes skills tap add KeaneYan/hermes-gateway-startup-notify
```

### Install the skill

```bash
hermes skills install gateway-startup-notify
```

### skills.sh / skills CLI path

If you are testing discovery through the external skills ecosystem, use:

```bash
npx skills add KeaneYan/hermes-gateway-startup-notify
```

That path is the one most relevant for **skills.sh leaderboard / telemetry-based discovery**.

## Search / Discovery Keywords

This repo is intentionally focused on these search intents:
- Hermes gateway
- gateway startup notification
- startup notify
- restart notification
- gateway:startup hook
- WeChat hook
- Weixin hook
- iLink bot API

## Repo Layout

This repo uses a **flat skills.sh-friendly layout**:

```text
hermes-gateway-startup-notify/
├── README.md
└── gateway-startup-notify/
    ├── SKILL.md
    ├── templates/
    │   ├── HOOK.yaml
    │   └── handler.py
    └── references/
        └── api-notes.md
```

Keeping each skill at the repo root helps external indexes like skills.sh pick it up correctly.

## What the Skill Includes

The `gateway-startup-notify` skill now includes:
- a ready-to-copy `HOOK.yaml`
- a ready-to-copy `handler.py`
- request-format notes for the WeChat / Weixin iLink API
- verification steps
- debugging and troubleshooting guidance

## Development

To edit locally:

```bash
git clone https://github.com/KeaneYan/hermes-gateway-startup-notify.git
cd hermes-gateway-startup-notify
```

Then update the skill files and push changes normally.
