# 💣 oddava's minesweeper

A feature-rich Minesweeper bot for Telegram with a WebApp frontend, multiple themes, and comprehensive admin tools.

**Version:** v1.4.0

## ✨ Features

### 🎮 Game
- **WebApp**: Smooth Minesweeper built with Vanilla JS and Telegram Web Apps
- **3 Difficulty Modes**: Beginner (9×9), Intermediate (16×16), Expert (16×30)
- **5 Themes**: Classic, Neon, Ocean, Retro, New Year Eve 🎆
- **Settings**: Theme & vibration preferences persist across sessions
- **Stats Tracking**: Best times, win count, game history

### 🛡️ Security
- **Anti-Cheat**: Validates `Telegram.initData` signatures
- **Time Validation**: Rejects impossible times (<3s)
- **Suspicious Activity Flagging**: Expert wins <30s get flagged
- **Rate Limiting**: Built-in API protection

### 📊 Admin & Monitoring
- **Admin Panel**: Role-based access (Superadmin/Admin)
- **Prometheus Metrics**: `/metrics` endpoint for monitoring
- **Grafana Dashboards**: Pre-configured dashboards included
- **Automated Backups**: PostgreSQL backups every 30 minutes

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- (Optional) Ngrok for local development

### Setup

```bash
# Clone the repo
git clone https://github.com/oddava/minesweeper-bot.git
cd minesweeper_bot

# Configure environment
cp .env.example .env
# Edit .env with your BOT_TOKEN and SUPERADMIN_ID

# Start with Docker
make compose-up
```

For production deployment, see [Deployment Guide](docs/DEPLOYMENT.md).

## 🔧 Bot Commands

| Command | Role | Description |
|---------|------|-------------|
| `/play` | User | Launch the game |
| `/profile` | User | View your stats |
| `/leaderboard` | User | Top players |
| `/changelog` | User | What's new |
| `/support` | User | Get help |
| `/admin` | Superadmin | Admin commands |
| `/admin add <id>` | Superadmin | Add an admin |
| `/admin remove <id>` | Superadmin | Remove an admin |
| `/broadcast <msg>` | Superadmin | Message all users |
| `/stats` | Admin | Bot health & stats |
| `/ban <id>` | Admin | Ban a user |
| `/unban <id>` | Admin | Unban a user |
| `/suspicious` | Admin | View flagged users |

## 🛠️ Development

```bash
# Install dependencies (requires uv)
make deps

# Run linters
make check

# Format code
make format

# Database migrations
make migrate

# View logs
make logs
```

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Bot Framework | Python 3.13, Aiogram 3.x |
| API | FastAPI |
| Database | PostgreSQL 14 (Async), PgBouncer |
| Cache/FSM | Redis 7 |
| WebApp | HTML5, CSS3, Vanilla JS |
| Reverse Proxy | Caddy (auto SSL) |
| Monitoring | Prometheus, Grafana |
| Containers | Docker Compose |

## 📁 Project Structure

```
minesweeper_bot/
├── bot/
│   ├── handlers/       # Command handlers
│   ├── middlewares/    # Rate limiting, i18n
│   ├── database/       # Models & repositories
│   ├── web_app/        # Game frontend (HTML/CSS/JS)
│   ├── api/            # FastAPI endpoints
│   └── core/           # Config & settings
├── configs/            # Prometheus, Grafana configs
├── migrations/         # Alembic migrations
├── docs/               # Documentation
└── docker-compose.yml
```

## 📝 License

MIT License
