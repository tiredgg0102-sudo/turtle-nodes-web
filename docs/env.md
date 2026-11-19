# Environment Variable Reference

All configuration is provided via environment variables (`.env` file). See `.env.example` for a template.

## Required

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret (long random string) |
| `ENCRYPTION_KEY` | Fernet key for encrypting credentials at rest |

## App

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | development | development \| staging \| production |
| `APP_DEBUG` | false | Enable debug mode & API docs |
| `HOST` | 0.0.0.0 | Bind host |
| `PORT` | 8000 | Bind port |
| `WORKERS` | 1 | Uvicorn workers |
| `DATABASE_URL` | sqlite:///./hosting.db | SQLAlchemy DB URL |
| `FRONTEND_URL` | http://localhost:8000 | Public frontend URL |
| `CORS_ORIGINS` | http://localhost:8000 | Comma-separated allowed origins |
| `COOKIE_SECURE` | false | Set true in production (HTTPS) |
| `COOKIE_SAMESITE` | lax | Cookie SameSite policy |

## Discord

| Variable | Description |
|----------|-------------|
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_GUILD_ID` | Discord server (guild) ID |
| `DISCORD_STAFF_ROLE_IDS` | Comma-separated staff role IDs |
| `DISCORD_ORDER_CHANNEL_ID` | Channel for order submissions |
| `DISCORD_STAFF_CHANNEL_ID` | Channel for staff notifications |
| `DISCORD_NOTIFICATIONS_CHANNEL_ID` | Webhook URL for notifications |
| `DISCORD_INVITE_URL` | Invite link shown on website |
| `BACKEND_URL` | Backend URL used by the bot |
| `BOT_API_KEY` | Shared secret for bot ↔ backend auth |

## Pterodactyl

| Variable | Description |
|----------|-------------|
| `PTERODACTYL_URL` | Your Pterodactyl panel URL |
| `PTERODACTYL_APP_API_KEY` | Application API key (admin scope) |
| `PTERODACTYL_DEFAULT_NODE_ID` | Default node for provisioning |
| `PTERODACTYL_DEFAULT_LOCATION_ID` | Default location |
| `PTERODACTYL_DEFAULT_NEST_ID` | Default nest |
| `PTERODACTYL_DEFAULT_EGG_ID` | Default egg |
| `PTERODACTYL_DEFAULT_RAM` | Default RAM (MB) |
| `PTERODACTYL_DEFAULT_CPU` | Default CPU (%) |
| `PTERODACTYL_DEFAULT_STORAGE` | Default storage (MB) |

## Email (optional)

| Variable | Description |
|----------|-------------|
| `SMTP_HOST` | SMTP server host |
| `SMTP_PORT` | SMTP port (587) |
| `SMTP_USERNAME` | SMTP username |
| `SMTP_PASSWORD` | SMTP password |
| `SMTP_FROM_EMAIL` | From address |
| `EMAIL_VERIFICATION_REQUIRED` | Require email verification on register |
