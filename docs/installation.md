# Installation Guide

## Development (local)

1. Copy `.env.example` to `.env` and fill in `SECRET_KEY` and `ENCRYPTION_KEY`.
2. `cd backend && python -m pip install -r requirements.txt`
3. `cd backend && python -m alembic upgrade head`
4. `cd backend && python -m app.scripts.seed`
5. `cd backend && python -m app.scripts.create_admin --email admin@example.com --password ChangeMe123 --username admin`
6. `cd backend && python -m uvicorn app.main:app --reload --port 8000`
7. Visit http://localhost:8000

## VPS (production)

Run on a fresh Ubuntu 22.04/24.04 or Debian 11/12/13 VPS:

```bash
curl -fsSL https://raw.githubusercontent.com/you/hosting-platform/main/installer/install.sh | sudo bash
```

Or download and run manually:

```bash
sudo bash installer/install.sh install
```

### Installer modes

| Mode | Command | Description |
|------|---------|-------------|
| Fresh install | `install.sh install` | Full installation |
| Repair | `install.sh repair` | Reinstall deps, re-init DB, restart services |
| Update | `install.sh update` | Back up DB, update code, run migrations |
| Reconfigure | `install.sh reconfigure` | Re-run config wizard |
| Diagnostics | `install.sh diagnostics` | Show service status and logs |
| Backup | `install.sh backup` | Create a backup archive |
| Uninstall | `install.sh uninstall` | Remove services (DB preserved) |

### Post-install

- Configure Pterodactyl: Admin Dashboard → Pterodactyl Integration → Test Connection.
- Configure Discord: set env vars, restart bot service.
- Create hosting plans: Admin Dashboard → Hosting Plans.
- Set up HTTPS: `certbot --nginx -d yourdomain.com`.
