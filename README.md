
# 💣 Minesweeper Telegram Bot

A feature-rich Minesweeper bot for Telegram with a Web App frontend, Anti-Cheat system, and comprehensive Admin Panel.

## ✨ Features

- **Web App Game**: Smooth Minesweeper built with Vanilla JS and Telegram Web Apps.
- **Game Modes**: Beginner (9x9), Intermediate (16x16), Expert (16x30).
- **Admin Panel**: Role-based access control (Superadmin/Admin).
- **Anti-Cheat System**:
  - Validates `Telegram.initData` signatures.
  - Rejects impossible times (< 3 seconds).
  - Flags suspicious activity (e.g. Expert wins < 30s).
- **Analytics**: Prometheus metrics endpoint (`/metrics`) and custom game stats.
- **Architecture**: Dockerized setup with PostgreSQL (Async), Redis, and PgBouncer.

## 🚀 Quick Setup

### 1. Prerequisites
- Docker & Docker Compose
- A Telegram Bot Token (@BotFather)
- An Ngrok account (for local development/webhooks)

### 2. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your details:
- `BOT_TOKEN`: Your Telegram bot token.
- `SUPERADMIN_ID`: Your Telegram user ID (get it from @userinfobot).
- `WEBHOOK_BASE_URL`: Your public HTTPS URL (e.g. Ngrok).

### 3. Run with Docker
```bash
docker compose up -d --build
```

### 4. Cloud Deployment (AWS/DigitalOcean)
For production setup with Webhooks and SSL, see the [Deployment Guide](docs/DEPLOYMENT.md).

### 5. Admin Setup
Upon first run, if your `SUPERADMIN_ID` is set correctly in `.env`, you will automatically be recognized as a Superadmin.

## 🔧 Commands

| Command | Role | Description |
|---------|------|-------------|
| `/play` | User | Start a game |
| `/profile` | User | View your stats |
| `/leaderboard` | User | View top players |
| `/admin` | Superadmin | Admin help menu |
| `/admin add <id>` | Superadmin | Promote a user to Admin |
| `/admin remove <id>` | Superadmin | Demote an Admin |
| `/broadcast <msg>` | Superadmin | Send a message to all users |
| `/config` | Superadmin | Debug current config |
| `/stats` | Admin | View bot health & stats |
| `/ban <id>` | Admin | Ban a cheater |
| `/unban <id>` | Admin | Unban a user |
| `/suspicious` | Admin | List flagged users |

## 🛡️ Security Checklists

- [x] **Secret Management**: Ensure `.env` is never committed (it is in `.gitignore`).
- [x] **Web App VALIDATION**: The API verifies `initData` to prevent spoofing.
- [x] **Rate Limiting**: Configured in API middleware.
- [x] **Infrastructure**: Database ports should not be exposed globally in production.

## 🏗️ Tech Stack

- **Backend**: Python 3.11, Aiogram 3.x, FastAPI (for Web App API & Webhooks).
- **Database**: PostgreSQL 14 (Async SQLAlchemy), Redis (FSM & Caching).
- **Frontend**: HTML5, CSS3, Vanilla JS.
- **Monitoring**: Prometheus.

## 📝 License

MIT License
