# Hosting Platform

A complete, production-ready hosting business platform built from scratch.

## Overview

This is a **completely new and independent project**. It is not derived from, and does not modify, any existing repository.

The platform provides:

- A premium public website (futuristic dark theme, neon green/cyan accents, glassmorphism)
- Customer authentication (register, login, password reset, email verification, secure sessions)
- Customer dashboard (services, orders, tickets, announcements, account & security settings, Pterodactyl & Discord connection)
- Admin dashboard (customers, services, orders, plans, products, Pterodactyl integration, Discord integration, tickets, announcements, logs, settings, diagnostics)
- Secure Pterodactyl panel integration (Application API + Client API)
- Discord ordering bot (slash commands, buttons, order approval/rejection)
- Automated service provisioning engine (background jobs, retries, idempotency)
- Support ticket system with Discord notifications
- Centralized notification system (website, Discord, email)
- Role-based access control, CSRF protection, rate limiting, encrypted credentials at rest, audit logging
- Professional VPS installation suite (fresh/repair/update/reconfigure/diagnostics/backup/restore/uninstall)
- Environment-based configuration (no hardcoded secrets)

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend API | Python 3.14 + FastAPI |
| Database | SQLAlchemy 2.x + Alembic migrations (SQLite default, PostgreSQL supported) |
| Auth | JWT (HttpOnly secure cookies) + bcrypt password hashing + CSRF double-submit |
| Frontend | Vanilla JavaScript SPA + Tailwind CSS (no build step / no Node required) |
| Discord Bot | discord.py (slash commands, buttons, selects) |
| Pterodactyl | Official Application API + Client API (server-side only) |
| Background Jobs | Asyncio job queue with retry & idempotency |
| Encryption | Fernet (symmetric) for credentials at rest |
| Logging | Structured logging with secret redaction |
| Installer | Bash (Ubuntu/Debian VPS) with premium terminal UI |

## Project Structure

```
hosting-platform/
├── backend/           # FastAPI application + migrations + tests
├── frontend/          # Vanilla JS SPA + Tailwind (served by backend)
├── bot/               # Discord ordering bot (discord.py)
├── installer/         # VPS installation suite (bash)
├── docs/              # Installation, administrator, API, Discord, Pterodactyl, troubleshooting
└── tests/             # Integration & unit tests
```

## Quick Start (Development)

### 1. Create environment file

```bash
cp .env.example .env
# Edit .env with your settings (see docs/env.md)
```

Required minimum in `.env`:

```env
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=replace-with-a-long-random-secret
ENCRYPTION_KEY=replace-with-a-fernet-key
DATABASE_URL=sqlite:///./hosting.db
FRONTEND_URL=http://localhost:8000
```

Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Install dependencies

```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Run database migrations

```bash
cd backend
alembic upgrade head
```

### 4. Create the first admin user

```bash
cd backend
python -m app.scripts.create_admin \
  --email admin@example.com \
  --password ChangeMe123! \
  --role admin
```

### 5. Start the server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000

### 6. Run tests

```bash
cd backend
python -m pytest tests/ -v
```

## Discord Bot

The Discord bot connects orders placed on the website to your Discord server for staff approval.

1. Create a Discord application and bot at https://discord.com/developers/applications
2. Enable the Message Content Intent and Slash Commands
3. Add `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID`, `DISCORD_STAFF_ROLE_IDS`, `DISCORD_CHANNEL_IDS` to `.env`
4. Run: `cd bot && python -m bot.main`

See `docs/discord.md` for full setup.

## Pterodactyl Integration

Connect to your existing Pterodactyl panel via its official APIs.

1. In Pterodactyl, create an Application API key (Admin area)
2. Add `PTERODACTYL_URL` and `PTERODACTYL_APP_API_KEY` to `.env`
3. Use Admin Dashboard → Pterodactyl Integration → Test Connection

Customers connect their own Client API key from Customer Dashboard → Pterodactyl Connection.

See `docs/pterodactyl.md`.

## VPS Installation

See `docs/installation.md` and run the installer on a fresh Ubuntu 22.04/24.04 or Debian 11/12 VPS:

```bash
curl -fsSL https://raw.githubusercontent.com/you/hosting-platform/main/installer/install.sh | sudo bash
```

## Documentation

- `docs/installation.md` — VPS install, repair, update, backup, restore
- `docs/administrator.md` — Admin dashboard guide
- `docs/api.md` — REST API reference
- `docs/discord.md` — Discord bot setup & commands
- `docs/pterodactyl.md` — Pterodactyl integration guide
- `docs/env.md` — Environment variable reference
- `docs/troubleshooting.md` — Common issues

## Security

- Passwords hashed with bcrypt (never plaintext)
- Sensitive credentials (API keys, bot tokens) encrypted at rest with Fernet
- JWT access tokens in HttpOnly, Secure, SameSite cookies
- CSRF double-submit protection on state-changing endpoints
- Rate limiting on auth endpoints
- Server-side authorization on every request
- Audit logging for admin actions
- Secrets redacted from logs

See `docs/security.md` (in `docs/`) for the security audit.

## License

Private — internal hosting business platform.
