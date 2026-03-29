# HyperTrace - Deployment Guide

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)
- Git

---

## Local Development

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd hyper-it

# Create environment file
cp backend/.env.example backend/.env
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Docker Deployment

### 1. Build and Run

```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2. Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI API server |
| frontend | 3000 | Next.js dashboard |
| db | 5432 | PostgreSQL database (optional) |

---

## Production Deployment

### Option 1: VPS / Cloud Server

#### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host/db"
export HYPERLIQUID_API_URL="https://api.hyperliquid.xyz"

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend

```bash
# Build for production
npm run build

# Start with PM2 or similar
npm start
```

### Option 2: Railway / Render / Fly.io

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Render
1. Connect GitHub repository
2. Create Web Service for backend (Python)
3. Create Static Site for frontend (Node.js)
4. Set environment variables

#### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy backend
fly launch --dockerfile backend/Dockerfile

# Deploy frontend
fly launch --dockerfile frontend/Dockerfile
```

---

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./hypertrace.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/hypertrace

# API Keys (optional - HyperLiquid doesn't require API key for public data)
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz
COINGECKO_API_KEY=your_key_here

# Application
APP_NAME=HyperTrace
DEBUG=false
LOG_LEVEL=INFO

# Scheduler
FETCH_INTERVAL_MINUTES=5

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://hypertrace.io
```

### Frontend (.env.local)
```env
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# App Config
NEXT_PUBLIC_APP_NAME=HyperTrace
NEXT_PUBLIC_REFRESH_INTERVAL=300000
```

---

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name hypertrace.io;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name hypertrace.io;

    # SSL certificates
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Database Setup

### SQLite (Development)
```bash
# Auto-created on first run
# No setup required
```

### PostgreSQL (Production)

```bash
# Create database
sudo -u postgres createdb hypertrace

# Create user
sudo -u postgres createuser -P hypertrace_user

# Run migrations
alembic upgrade head
```

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Expected response
{"status": "healthy", "timestamp": "2026-03-30T12:00:00Z"}
```

### Logs

```bash
# View backend logs
tail -f backend/logs/app.log

# View with journalctl (systemd)
journalctl -u hypertrace-backend -f
```

---

## Backup and Restore

### Database Backup
```bash
# SQLite
cp hypertrace.db hypertrace.db.backup.$(date +%Y%m%d)

# PostgreSQL
pg_dump hypertrace > backup.sql
```

### Database Restore
```bash
# SQLite
cp hypertrace.db.backup.20260330 hypertrace.db

# PostgreSQL
psql hypertrace < backup.sql
```

---

## Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check port availability
lsof -i :8000

# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### Frontend build errors
```bash
# Clear cache
rm -rf node_modules .next
npm install

# Check Node version
node --version  # Should be 18+
```

#### Database connection issues
```bash
# Check SQLite permissions
ls -la hypertrace.db

# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"
```

---

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong DATABASE_URL password
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Disable DEBUG mode in production
