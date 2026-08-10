<p align="center">
  <img src="docs/public/logo.svg" width="80" height="80" alt="TG-SignPulse Logo">
</p>

<h1 align="center">TG-SignPulse</h1>

> [!NOTE]
> **v1.0.0 First Release:** This is the first official TG-SignPulse release. For a fresh deployment, use a clean `data/` directory. If you are migrating from another branch or older data, back up your data first.

<p align="center">
  <strong>Telegram Multi-Account Automation Panel</strong><br>
  Check-ins · Action Workflows · Keyword Monitoring · AI Verification
</p>

<p align="center">
  <a href="https://github.com/yuehex15/TG-SignPulse/releases"><img src="https://img.shields.io/badge/version-v1.0.1-blue" alt="Version"></a>
  <a href="https://github.com/yuehex15/TG-SignPulse/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-BSD--3--Clause-green" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10--3.13-blue" alt="Python">
  <img src="https://img.shields.io/badge/node-20+-green" alt="Node.js">
  <a href="https://github.com/yuehex15/TG-SignPulse/pkgs/container/tg-signpulse"><img src="https://img.shields.io/badge/ghcr.io-available-purple" alt="GHCR"></a>
</p>

<p align="center">
  <a href="README.md">中文说明</a> · <a href="docs/README.md">Documentation</a> · <a href="docs/guide/quick-start.md">Quick Start</a> · <a href="#changelog">Changelog</a>
</p>

---

## Overview

TG-SignPulse is a Telegram automation panel. Manage multiple accounts, configure automated check-in tasks, and run them on fixed schedules or random time ranges — all from a web UI.

> 🤖 AI-powered: Integrated with OpenAI-compatible APIs for image recognition, math challenges, OCR, and more.

---

## Features

| Area | Capability |
|------|-----------|
| **Account Management** | Multi-account login (SMS/QR), proxy, status checks, re-login |
| **Task Workflows** | Fixed / random-range / listen-trigger execution modes |
| **Action Types** | Send text, click button, send dice, AI vision, AI calculate, keyword monitor |
| **Topic Support** | Send and filter by Telegram group Thread ID |
| **Keyword Monitoring** | Contains/exact/regex match → Telegram Bot, forward, Bark, custom URL, continue actions |
| **Notifications** | Task failure, invalid session, login, keyword match alerts |
| **Operations** | Docker deploy, persistent data, health checks, config import/export |

---

## Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│  Frontend          Vue 3 + Vue Router + Pinia           │
│                    Tailwind CSS 4 + Lucide Icons         │
│                    Vite + PWA                            │
├─────────────────────────────────────────────────────────┤
│  Backend           FastAPI + Uvicorn                     │
│                    SQLAlchemy + SQLite (WAL)             │
│                    APScheduler (AsyncIO)                 │
│                    JWT + TOTP 2FA + bcrypt               │
├─────────────────────────────────────────────────────────┤
│  Telegram Engine   Pyrogram / Kurigram                   │
│                    Session File / String dual mode       │
├─────────────────────────────────────────────────────────┤
│  AI Integration    OpenAI SDK (compatible APIs)          │
│                    Vision / OCR / Math / Inference       │
├─────────────────────────────────────────────────────────┤
│  Infrastructure    Docker Multi-stage Build              │
│                    GitHub Actions CI/CD                   │
│                    GHCR Container Registry               │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Docker 24+ with Docker Compose
- At least one Telegram account

### One-command Deploy

```bash
docker run -d \
  --name tg-signpulse \
  --restart unless-stopped \
  -p 8080:8080 \
  -v $(pwd)/data:/data \
  -e TZ=Asia/Shanghai \
  -e APP_SECRET_KEY=$(openssl rand -base64 32) \
  -e ADMIN_PASSWORD=your_strong_password \
  ghcr.io/yuehex15/tg-signpulse:latest
```

### Docker Compose

```yaml
services:
  app:
    image: ghcr.io/yuehex15/tg-signpulse:latest
    container_name: tg-signpulse
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
    environment:
      - TZ=Asia/Shanghai
      - APP_SECRET_KEY=your_secret_key
      - ADMIN_PASSWORD=your_strong_password
```

```bash
docker compose up -d
```

### Login

Open `http://YOUR_SERVER_IP:8080`

- Username: `admin`
- Password: your `ADMIN_PASSWORD` (or check `data/.admin_bootstrap_password` if not set)

---

## Project Structure

```text
TG-SignPulse/
├── backend/            # FastAPI backend
│   ├── api/            #   API routes
│   ├── core/           #   Config, auth, database
│   ├── models/         #   SQLAlchemy models
│   ├── services/       #   Business logic
│   ├── scheduler/      #   APScheduler
│   └── utils/          #   Utilities
├── tg_signer/          # Telegram automation engine
│   ├── core.py         #   Sign-in execution core
│   ├── config.py       #   Task config models (V1→V2→V3)
│   └── ai_tools.py     #   AI tool integration
├── frontend/           # Vue 3 frontend
├── docker/             # Docker entrypoint
├── docs/               # Documentation (VitePress)
├── Dockerfile          # Multi-stage build
├── docker-compose.yml  # Compose orchestration
└── pyproject.toml      # Python project config
```

---

## Documentation

Full documentation at [docs/README.md](docs/README.md):

- [Quick Start](docs/guide/quick-start.md) — Deploy and create your first task in 5 minutes
- [Docker Deployment](docs/deploy/docker.md) — Images, Compose, reverse proxy, upgrades
- [Configuration Reference](docs/reference/configuration.md) — Env vars, data directory, config files
- [Account Management](docs/guide/accounts.md) — Login methods, proxy, session modes
- [Task Workflows](docs/guide/tasks.md) — Action types, execution modes, multi-account sharing
- [AI Actions](docs/guide/ai.md) — OpenAI config and custom prompts
- [Keyword Monitoring](docs/guide/keyword-monitor.md) — Match rules, push channels, continue actions
- [Architecture](docs/reference/architecture.md) — System design and data flow

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_SECRET_KEY` | JWT secret (required in production) | Auto-generated |
| `ADMIN_PASSWORD` | Initial admin password | Random |
| `APP_DATA_DIR` | Data directory | `/data` |
| `TZ` | Timezone | `Asia/Shanghai` |
| `TG_SESSION_MODE` | Session mode `file`/`string` | `file` |
| `TG_GLOBAL_CONCURRENCY` | Global concurrency limit | `1` |
| `TG_PROXY` | Global Telegram proxy | None |

See [Configuration Reference](docs/reference/configuration.md) for the full list.

---

## Local Development

```bash
# Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"    # or: uv pip install -e ".[dev]"
# Optional: build frontend so one process serves UI + API
cd frontend && npm ci && npm run build && cd ..
export APP_WEB_DIR="$PWD/frontend/dist"
export APP_DATA_DIR="$PWD/data"
export APP_SECRET_KEY=dev-secret
export ADMIN_PASSWORD=admin123
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080

# Frontend HMR (separate terminal; Vite proxies /api to 8080)
cd frontend
npm ci
npm run dev
```

- Python 3.10–3.13 (3.12 recommended)
- Node.js 20+
- Python 3.14+ is not recommended (Telegram runtime deps not yet compatible)
- Local image build: `docker compose -f docker-compose.panel.yml up -d --build`
- Smoke tests: `pytest -q`

---

## Health Checks

```bash
curl http://127.0.0.1:8080/healthz   # Quick health check
curl http://127.0.0.1:8080/readyz    # Readiness check
```

---

## Changelog

### v1.0.1 (2026-08-10)

**Release & engineering fixes**
- Fix local install (`pip install -e ".[dev]"`), Compose secrets, and panel build compose
- Unify defaults: port `8080`, CORS, timezone `Asia/Shanghai`; drop Next.js leftovers; add `APP_WEB_DIR`
- Remove local `jose`/`pyotp` shims; use official PyPI packages
- Add CI smoke (frontend build + backend pytest); push GHCR `:latest` on main/tag
- Public repo + `v1.0.1` release pipeline

### v1.0.0 (2026-05-16)

**Versioned releases**: Starting from this version, the project uses semantic versioning.

**Bug Fixes**
- Fixed QR login getting stuck on "processing..." after a successful scan.
- Fixed task log modal not showing historical logs after clicking "View Logs".
- Fixed missing target chat avatars for multi-account tasks using the `*` wildcard.
- Fixed edit/delete/run failures for multi-account tasks when `account_name` was empty.

**Code Quality**
- Replaced all DEBUG print statements with structured logging
- Fixed garbled error messages in `accounts.py`
- Fixed SPA fallback incorrectly redirecting to dev server in production
- Docker Compose: removed deprecated `version` field, added tmpfs mounts
- Moved `vite-plugin-pwa` to devDependencies

**Documentation**
- Rewrote README with tech stack overview and project structure
- Updated docs with deployment guide and configuration reference
- Fixed default password documentation inconsistency

---

## Acknowledgements

Based on [tg-signer](https://github.com/amchii/tg-signer) by [amchii](https://github.com/amchii), heavily refactored and extended.

---

## License

[BSD-3-Clause](LICENSE)
