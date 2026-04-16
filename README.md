# Hermes Skills

Custom skills for Hermes Agent.

## Available Skills

### `gateway-startup-notify`
Send a WeChat notification through the iLink Bot API whenever the Hermes gateway finishes starting up.

Good for:
- confirming a remote gateway restarted successfully
- getting a push message after deploy / reboot
- monitoring always-on Hermes instances

## Install

### Install this repo as a tap

```bash
hermes skills tap add KeaneYan/hermes-skills
```

### Install the skill

```bash
hermes skills install gateway-startup-notify
```

If your local setup still uses the npm-based installer flow, this repo can also be discovered via:

```bash
npx skills add KeaneYan/hermes-skills
```

## Repo Layout

This repo uses a **flat skills.sh-friendly layout**:

```text
hermes-skills/
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

## Usage Notes

After installation, load the skill in Hermes and follow the setup steps in the skill doc. The `gateway-startup-notify` skill now includes:

- a ready-to-copy `HOOK.yaml`
- a ready-to-copy `handler.py`
- request-format notes for the iLink API
- verification / debugging steps

## Development

To edit locally:

```bash
git clone https://github.com/KeaneYan/hermes-skills.git
cd hermes-skills
```

Then update the skill files and push changes normally.
