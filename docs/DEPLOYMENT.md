# 🚀 Deployment Guide

Deploy oddava's minesweeper bot to a cloud server (AWS, DigitalOcean, etc.) with automatic SSL.

## Prerequisites

- A VPS (Ubuntu 22.04 recommended, t3.micro works)
- A domain name pointing to your server
- Ports 80, 443 open in firewall

## 1. Server Setup

```bash
# SSH into your server
ssh ubuntu@your-server-ip

# Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker $USER
# Log out and back in for group changes
```

## 2. Deploy the Bot

```bash
# Clone repository
git clone <your-repo-url>
cd minesweeper_bot

# Configure environment
cp .env.example .env
nano .env
```

### Required `.env` settings:

```bash
BOT_TOKEN="your-bot-token"
SUPERADMIN_ID=your-telegram-id
USE_WEBHOOK=True
WEBHOOK_BASE_URL="https://your-domain.com"
DOMAIN="your-domain.com"
CADDY_EMAIL="your-email@example.com"
DB_HOST="pgbouncer"
```

### Start services:

```bash
docker compose up -d --build
```

## 3. SSL (Automatic with Caddy)

Caddy handles SSL automatically. Ensure:
1. Your domain's A record points to the server IP
2. Ports 80 and 443 are open
3. `DOMAIN` and `CADDY_EMAIL` are set in `.env`

Certificates are provisioned on first request.

## 4. Verify Deployment

```bash
# Check all services are running
docker compose ps

# Check bot logs
docker compose logs bot -f

# Check webhook status
curl https://your-domain.com/health
```

## 5. Monitoring

### Prometheus
Access via SSH tunnel (recommended):
```bash
ssh -L 9090:localhost:9090 ubuntu@your-server-ip
# Then open http://localhost:9090
```

### Grafana
- URL: `https://grafana.your-domain.com` (if configured in Caddyfile)
- Or via SSH tunnel: `ssh -L 3000:localhost:3000 ubuntu@your-server-ip`
- Default login: Check `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD` in `.env`

## 6. Maintenance

### Updates
```bash
git pull
docker compose up -d --build
```

### Backups
```bash
# List backups
make list-backups

# Manual backup
make backup

# Restore (replace filename)
make restore args=/backups/daily/bot_db-20241227-120000.sql.gz
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs bot -f
```

## Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Don't expose DB ports (5432) publicly
- [ ] Use SSH tunnel for Prometheus/Grafana
- [ ] Keep Docker and OS updated
- [ ] Enable UFW firewall (allow 22, 80, 443 only)
