# 🚀 AWS Cloud Deployment Guide

This guide walks you through deploying the Minesweeper Bot to **AWS EC2** using Webhooks and a secure HTTPS setup.

## 1. Prepare AWS Environment
1. **Launch EC2 Instance**: Use Ubuntu 22.04 LTS (t3.micro is enough for start).
2. **Security Group**:
   - Allow **SSH (22)** from your IP.
   - Allow **HTTP (80)** and **HTTPS (443)** from anywhere.
   - (Optional) Allow **3000** (Grafana) and **9090** (Prometheus) if you want direct access (better to use SSH tunnel or Nginx proxy).

## 2. Server Setup
Connect via SSH and install dependencies:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose git nginx python3-certbot-nginx
```

## 3. Deployment
1. **Clone & Config**:
   ```bash
   git clone <your-repo-url>
   cd minesweeper_bot
   cp .env.example .env
   # Edit .env: set USE_WEBHOOK=True, WEBHOOK_BASE_URL=https://your-domain.com
   ```
2. **Start Services**:
   ```bash
   make compose-up
   ```

## 4. HTTPS & Automatic SSL (Caddy)
The bot now uses **Caddy** to automatically handle SSL certificates from Let's Encrypt.
1. **Configure .env**: Ensure `DOMAIN` and `CADDY_EMAIL` are set.
2. **DNS**: Point your domain's A record to the AWS EC2 IP.
3. **Run**: Caddy is part of the `docker-compose.yml`. It will automatically provision an SSL certificate for your domain on first run.

## 📈 Monitoring & Metrics

### 1. Accessing Prometheus
- **Direct**: `http://your-server-ip:9090` (if port is open in Security Group).
- **SSH Tunnel (Highly Recommended)**:
  ```bash
  ssh -L 9090:localhost:9090 ubuntu@your-server-ip
  ```
  Then visit `http://localhost:9090` on your machine.

### 2. Accessing Grafana
- **URL**: `http://your-server-ip:3000`
- **Default Login**: Defined in `.env` (`GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD`).
- **Dashboard**: We have pre-configured dashboards in `configs/grafana/dashboards`.

### 3. Minesweeper Metrics
The bot exposes:
- **`minesweeper_games_total`**: Counter of games played (labels: `mode`, `status`).
- Standard Python & Process metrics.
