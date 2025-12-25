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

## 4. HTTPS (Nginx & SSL)
Telegram **requires** HTTPS for webhooks.
1. **Configure Nginx**:
   Create `/etc/nginx/sites-available/bot`:
   ```nginx
   server {
       server_name your-domain.com;
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
2. **Enable & SSL**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
   sudo certbot --nginx -d your-domain.com
   ```

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
