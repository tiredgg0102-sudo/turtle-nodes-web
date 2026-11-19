#!/usr/bin/env bash
#
# Hosting Platform - Professional VPS Installer
# Supports: Ubuntu 22.04/24.04, Debian 11/12/13
#
set -euo pipefail

# ---------------- Branding ----------------
APP_NAME="Hosting Platform"
APP_VERSION="1.0.0"
INSTALL_DIR="/opt/hosting-platform"
BACKEND_DIR="$INSTALL_DIR/backend"
FRONTEND_DIR="$INSTALL_DIR/frontend"
BOT_DIR="$INSTALL_DIR/bot"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="hosting-platform"
BOT_SERVICE_NAME="hosting-platform-bot"

# ---------------- Colors ----------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BLUE='\033[0;34m'; MAGENTA='\033[0;35m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[ OK ]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[FAIL]${NC} $*"; }
step()  { echo -e "\n${BOLD}${MAGENTA}▶ $*${NC}"; }

banner() {
  clear
  echo -e "${GREEN}"
  cat <<'EOF'
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║        H O S T I N G   P L A T F O R M   I N S T A L L E R  ║
  ║                                                              ║
  ║        Premium Hosting Business Platform  v1.0.0              ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
EOF
  echo -e "${NC}"
  echo -e "${DIM}  Environment: $(uname -s) $(uname -m) | $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')${NC}"
  echo
}

# ---------------- Checks ----------------
require_root() {
  if [[ $EUID -ne 0 ]]; then
    err "This installer must be run as root (use sudo)."
    exit 1
  fi
  ok "Running as root"
}

detect_os() {
  step "Detecting operating system"
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_ID="$ID"
    OS_VERSION="$VERSION_ID"
  else
    err "Cannot detect OS (/etc/os-release missing)."
    exit 1
  fi
  case "$OS_ID" in
    ubuntu|debian) ok "Detected $PRETTY_NAME" ;;
    *) err "Unsupported OS: $OS_ID. Supported: Ubuntu 22.04/24.04, Debian 11/12/13."; exit 1 ;;
  esac
  # Verify supported versions
  case "$OS_ID:$OS_VERSION" in
    ubuntu:22.04|ubuntu:24.04|debian:11|debian:12|debian:13) ok "Version $OS_VERSION is supported" ;;
    *) warn "Version $OS_VERSION is not in the tested list; continuing with best effort." ;;
  esac
}

detect_arch() {
  step "Detecting architecture"
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64|aarch64) ok "Architecture: $ARCH" ;;
    *) err "Unsupported architecture: $ARCH"; exit 1 ;;
  esac
}

check_resources() {
  step "Checking system resources"
  RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
  DISK_GB=$(df -BG / | awk 'NR==2{print $4}' | tr -d 'G')
  CPU_CORES=$(nproc)
  info "RAM: ${RAM_MB}MB | Disk free: ${DISK_GB}GB | CPU cores: ${CPU_CORES}"
  if [[ $RAM_MB -lt 1024 ]]; then warn "Less than 1GB RAM detected. Performance may be degraded."; fi
  if [[ $DISK_GB -lt 5 ]]; then err "Less than 5GB free disk. Aborting."; exit 1; fi
  ok "Resource check passed"
}

check_network() {
  step "Checking network connectivity"
  if ! ping -c 1 -W 5 8.8.8.8 >/dev/null 2>&1; then
    err "No network connectivity to 8.8.8.8"; exit 1
  fi
  ok "Network connectivity OK"
  if ! getent hosts github.com >/dev/null 2>&1; then
    warn "DNS resolution for github.com failed; package installs may fail."
  else
    ok "DNS resolution OK"
  fi
}

check_virt() {
  step "Detecting virtualization"
  if command -v systemd-detect-virt >/dev/null 2>&1; then
    VIRT=$(systemd-detect-virt 2>/dev/null || echo "unknown")
    info "Virtualization: $VIRT"
    case "$VIRT" in
      kvm|qemu|vmware|microsoft|oracle|xen) ok "Full virtualization detected ($VIRT)" ;;
      lxc|openvz) warn "Container virtualization ($VIRT) detected. Some services may require capabilities not available in containers." ;;
      none) ok "Bare metal detected" ;;
      *) warn "Unknown virtualization: $VIRT" ;;
    esac
  else
    warn "systemd-detect-virt not available; skipping virtualization detection."
  fi
}

check_conflicts() {
  step "Checking for port conflicts"
  for port in 80 443 8000; do
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
      warn "Port $port is already in use."
    else
      ok "Port $port is free"
    fi
  done
}

# ---------------- Dependencies ----------------
install_deps() {
  step "Installing system dependencies"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-dev \
    build-essential libssl-dev libffi-dev \
    nginx certbot python3-certbot-nginx \
    git curl wget ca-certificates \
    sqlite3
  ok "System dependencies installed"
}

# ---------------- Application setup ----------------
setup_app() {
  step "Setting up application directory"
  mkdir -p "$INSTALL_DIR"
  # If source is provided via INSTALL_SOURCE env, copy; else assume bundled.
  if [[ -n "${INSTALL_SOURCE:-}" && -d "$INSTALL_SOURCE" ]]; then
    cp -a "$INSTALL_SOURCE/." "$INSTALL_DIR/"
    ok "Application files copied from $INSTALL_SOURCE"
  else
    warn "INSTALL_SOURCE not set. Place application files in $INSTALL_DIR manually before running repair/configure."
  fi
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  if [[ -f "$BACKEND_DIR/requirements.txt" ]]; then
    "$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
  fi
  if [[ -f "$BOT_DIR/requirements.txt" ]]; then
    "$VENV_DIR/bin/pip" install -r "$BOT_DIR/requirements.txt"
  fi
  ok "Python environment ready"
}

# ---------------- Configuration wizard ----------------
configure() {
  step "Configuration wizard"
  ENV_FILE="$INSTALL_DIR/.env"
  if [[ -f "$ENV_FILE" ]]; then
    warn "Existing .env found; backing up to .env.bak"
    cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%s)"
  fi

  read -rp "Website domain (e.g. hosting.example.com): " DOMAIN
  read -rp "Application port [8000]: " APP_PORT
  APP_PORT=${APP_PORT:-8000}
  read -rp "Database URL [sqlite:///./hosting.db]: " DB_URL
  DB_URL=${DB_URL:-sqlite:///./hosting.db}

  # Generate secrets
  SECRET_KEY=$("$VENV_DIR/bin/python" -c "import secrets; print(secrets.token_hex(64))")
  ENCRYPTION_KEY=$("$VENV_DIR/bin/python" -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
  BOT_API_KEY=$("$VENV_DIR/bin/python" -c "import secrets; print(secrets.token_hex(32))")

  read -rp "Discord bot token (leave empty to skip): " DISCORD_BOT_TOKEN
  read -rp "Discord guild ID: " DISCORD_GUILD_ID
  read -rp "Discord staff role IDs (comma-separated): " DISCORD_STAFF_ROLE_IDS
  read -rp "Pterodactyl panel URL: " PTERODACTYL_URL
  read -rp "Pterodactyl Application API key: " PTERODACTYL_APP_API_KEY
  read -rp "Admin email: " ADMIN_EMAIL
  read -rsp "Admin password: " ADMIN_PASSWORD
  echo

  cat > "$ENV_FILE" <<EOF
APP_ENV=production
APP_DEBUG=false
APP_NAME=$APP_NAME
APP_VERSION=$APP_VERSION
HOST=0.0.0.0
PORT=$APP_PORT
WORKERS=2

SECRET_KEY=$SECRET_KEY
ENCRYPTION_KEY=$ENCRYPTION_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=30
BCRYPT_ROUNDS=12

DATABASE_URL=$DB_URL

FRONTEND_URL=https://$DOMAIN
CORS_ORIGINS=https://$DOMAIN
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=

RATE_LIMIT_LOGIN=10
RATE_LIMIT_REGISTER=5
RATE_LIMIT_WINDOW_SECONDS=60

SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=$APP_NAME
EMAIL_VERIFICATION_REQUIRED=false

DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
DISCORD_GUILD_ID=$DISCORD_GUILD_ID
DISCORD_STAFF_ROLE_IDS=$DISCORD_STAFF_ROLE_IDS
DISCORD_INVITE_URL=
BACKEND_URL=http://127.0.0.1:$APP_PORT
BOT_API_KEY=$BOT_API_KEY

PTERODACTYL_URL=$PTERODACTYL_URL
PTERODACTYL_APP_API_KEY=$PTERODACTYL_APP_API_KEY
PTERODACTYL_API_TIMEOUT=30

PROVISIONING_MAX_ATTEMPTS=5
PROVISIONING_RETRY_BACKOFF_SECONDS=30
EOF
  chmod 600 "$ENV_FILE"
  ok "Configuration written to $ENV_FILE"

  # Store admin creds for post-install
  echo "$ADMIN_EMAIL" > "$INSTALL_DIR/.admin_email"
  echo "$ADMIN_PASSWORD" > "$INSTALL_DIR/.admin_password"
  chmod 600 "$INSTALL_DIR/.admin_email" "$INSTALL_DIR/.admin_password"
}

# ---------------- Database ----------------
init_db() {
  step "Initializing database"
  cd "$BACKEND_DIR"
  "$VENV_DIR/bin/alembic" upgrade head
  "$VENV_DIR/bin/python" -m app.scripts.seed
  ADMIN_EMAIL=$(cat "$INSTALL_DIR/.admin_email")
  ADMIN_PASSWORD=$(cat "$INSTALL_DIR/.admin_password")
  "$VENV_DIR/bin/python" -m app.scripts.create_admin --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD" --username admin || true
  ok "Database initialized"
}

# ---------------- systemd services ----------------
setup_services() {
  step "Configuring systemd services"
  cat > "/etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=Hosting Platform Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port \${PORT} --workers \${WORKERS}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

  if [[ -n "${DISCORD_BOT_TOKEN:-}" ]]; then
    cat > "/etc/systemd/system/$BOT_SERVICE_NAME.service" <<EOF
[Unit]
Description=Hosting Platform Discord Bot
After=network.target $SERVICE_NAME.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$VENV_DIR/bin/python -m bot.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  fi

  systemctl daemon-reload
  systemctl enable "$SERVICE_NAME"
  systemctl restart "$SERVICE_NAME"
  if [[ -f "/etc/systemd/system/$BOT_SERVICE_NAME.service" ]]; then
    systemctl enable "$BOT_SERVICE_NAME"
    systemctl restart "$BOT_SERVICE_NAME"
  fi
  ok "Services configured and started"
}

# ---------------- Reverse proxy ----------------
setup_proxy() {
  step "Configuring reverse proxy (nginx)"
  DOMAIN=$(grep -E '^FRONTEND_URL=' "$INSTALL_DIR/.env" | sed 's#FRONTEND_URL=https://##')
  PORT=$(grep -E '^PORT=' "$INSTALL_DIR/.env" | cut -d= -f2)
  cat > "/etc/nginx/sites-available/$SERVICE_NAME" <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
}
EOF
  ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/$SERVICE_NAME"
  rm -f /etc/nginx/sites-enabled/default
  nginx -t && systemctl reload nginx
  ok "Nginx configured"
  info "Run 'certbot --nginx -d $DOMAIN' to enable HTTPS."
}

# ---------------- Verification ----------------
verify() {
  step "Post-installation verification"
  PORT=$(grep -E '^PORT=' "$INSTALL_DIR/.env" | cut -d= -f2)
  sleep 3
  if curl -fsS "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then
    ok "Backend health endpoint responding"
  else
    err "Backend health endpoint not responding"
  fi
  if systemctl is-active --quiet "$SERVICE_NAME"; then
    ok "Backend service is active"
  else
    err "Backend service is NOT active"
  fi
  if [[ -f "/etc/systemd/system/$BOT_SERVICE_NAME.service" ]]; then
    if systemctl is-active --quiet "$BOT_SERVICE_NAME"; then
      ok "Discord bot service is active"
    else
      warn "Discord bot service is NOT active (check token)"
    fi
  fi
  if nginx -t >/dev/null 2>&1; then
    ok "Nginx configuration valid"
  else
    warn "Nginx configuration has errors"
  fi
  echo
  echo -e "${GREEN}${BOLD}Installation complete!${NC}"
  echo -e "  Admin panel:  https://$DOMAIN"
  echo -e "  Admin email:  $(cat $INSTALL_DIR/.admin_email)"
  echo -e "  Config file:  $INSTALL_DIR/.env"
  echo
}

# ---------------- Repair / Update / etc. ----------------
repair() {
  step "Repair mode"
  setup_app
  init_db
  setup_services
  ok "Repair complete"
}

update() {
  step "Update mode"
  warn "Back up your database before updating."
  if [[ -f "$BACKEND_DIR/hosting.db" ]]; then
    cp "$BACKEND_DIR/hosting.db" "$BACKEND_DIR/hosting.db.bak.$(date +%s)"
    ok "Database backed up"
  fi
  setup_app
  cd "$BACKEND_DIR"
  "$VENV_DIR/bin/alembic" upgrade head
  setup_services
  ok "Update complete"
}

diagnostics() {
  banner
  echo "Service status:"
  systemctl status "$SERVICE_NAME" --no-pager || true
  echo
  echo "Recent logs:"
  journalctl -u "$SERVICE_NAME" -n 30 --no-pager || true
}

uninstall() {
  step "Uninstall mode"
  read -rp "This will remove the application (database preserved). Continue? [y/N] " confirm
  [[ "$confirm" == "y" || "$confirm" == "Y" ]] || { info "Aborted."; exit 0; }
  systemctl stop "$SERVICE_NAME" "$BOT_SERVICE_NAME" 2>/dev/null || true
  systemctl disable "$SERVICE_NAME" "$BOT_SERVICE_NAME" 2>/dev/null || true
  rm -f "/etc/systemd/system/$SERVICE_NAME.service" "/etc/systemd/system/$BOT_SERVICE_NAME.service"
  rm -f "/etc/nginx/sites-enabled/$SERVICE_NAME" "/etc/nginx/sites-available/$SERVICE_NAME"
  systemctl daemon-reload
  warn "Application files remain in $INSTALL_DIR (database preserved). Remove manually if desired."
  ok "Uninstall complete"
}

backup() {
  step "Backup"
  TS=$(date +%Y%m%d_%H%M%S)
  DEST="$INSTALL_DIR/backups/backup_$TS"
  mkdir -p "$DEST"
  cp "$INSTALL_DIR/.env" "$DEST/" 2>/dev/null || true
  if [[ -f "$BACKEND_DIR/hosting.db" ]]; then cp "$BACKEND_DIR/hosting.db" "$DEST/"; fi
  tar -czf "$DEST.tar.gz" -C "$INSTALL_DIR/backups" "backup_$TS"
  rm -rf "$DEST"
  ok "Backup created: $DEST.tar.gz"
}

# ---------------- Main ----------------
MODE="${1:-install}"
case "$MODE" in
  install)
    banner
    require_root
    detect_os
    detect_arch
    check_resources
    check_network
    check_virt
    check_conflicts
    install_deps
    setup_app
    configure
    init_db
    setup_services
    setup_proxy
    verify
    ;;
  repair)     banner; require_root; repair ;;
  update)     banner; require_root; update ;;
  reconfigure) banner; require_root; configure; setup_services ;;
  diagnostics) diagnostics ;;
  uninstall)  banner; require_root; uninstall ;;
  backup)     backup ;;
  restore)    warn "Restore: extract your backup tar.gz into $INSTALL_DIR and run repair." ;;
  *)
    echo "Usage: $0 {install|repair|update|reconfigure|diagnostics|uninstall|backup|restore}"
    exit 1
    ;;
esac
