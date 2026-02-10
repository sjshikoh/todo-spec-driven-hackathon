# Deployment Specification

## Overview

This specification covers deployment configuration, environment variables, dependencies, and Docker setup for Phase III.

## Environment Variables

### Backend: `.env`

```bash
# ============ Phase II (Existing) ============

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# JWT Authentication
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Server
HOST=0.0.0.0
PORT=8000

# ============ Phase III (New) ============

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# MCP Configuration
ENABLE_MCP=true

# AI Features
ENABLE_AI_CHAT=true
AI_STREAM_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

### Frontend: `.env.local`

```bash
# Backend API URL
BACKEND_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_AI_CHAT_ENABLED=true

# Optional: Analytics
NEXT_PUBLIC_ANALYTICS_ID=
```

### Environment Variable Descriptions

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | string | None | OpenAI API key (required for AI features) |
| `OPENAI_MODEL` | string | `gpt-4-turbo-preview` | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | int | 4096 | Max tokens per response |
| `OPENAI_TEMPERATURE` | float | 0.7 | Sampling temperature (0-2) |
| `ENABLE_MCP` | bool | false | Enable MCP server |
| `ENABLE_AI_CHAT` | bool | false | Enable AI chat endpoints |
| `AI_STREAM_ENABLED` | bool | true | Enable streaming responses |

---

## Dependencies

### Backend: `requirements.txt`

```txt
# ============ Phase II (Existing) ============
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# ============ Phase III (New) ============

# AI & MCP
openai==1.54.0              # OpenAI SDK with Agents support
mcp==1.1.0                  # Model Context Protocol SDK

# HTTP & WebSockets
httpx==0.27.0               # Async HTTP client (for OpenAI SDK)
websockets==12.0            # WebSocket support

# Utilities
python-dotenv==1.0.0        # Environment variable loading (if not already included)
```

### Frontend: `package.json` (Additions)

```json
{
  "dependencies": {
    "@ai-sdk/openai": "^0.0.66",
    "@ai-sdk/react": "^0.0.62",
    "ai": "^3.4.0"
  }
}
```

### Installation Commands

```bash
# Backend
cd /home/shaista/todo-spec-driven-hackathon
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## Configuration Module

### File: `src/config.py` (NEW)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Phase II and Phase III settings are combined in this single config.
    """

    # ============ Phase II Settings ============

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # ============ Phase III Settings ============

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.7

    # MCP
    enable_mcp: bool = False

    # AI Features
    enable_ai_chat: bool = False
    ai_stream_enabled: bool = True

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_ai_config(self) -> list[str]:
        """
        Validate AI configuration and return list of warnings.

        Returns:
            List of warning messages (empty if all valid)
        """
        warnings = []

        if self.enable_ai_chat and not self.openai_api_key:
            warnings.append("⚠️  ENABLE_AI_CHAT is true but OPENAI_API_KEY is not set")

        if self.enable_ai_chat and not self.enable_mcp:
            warnings.append("⚠️  ENABLE_AI_CHAT is true but ENABLE_MCP is false")

        return warnings


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
```

### Update: `src/main.py`

```python
# Add at top
from src.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add after app creation
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting Todo API")
    logger.info(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'local'}")

    # Validate AI configuration
    warnings = settings.validate_ai_config()
    for warning in warnings:
        logger.warning(warning)

    # Log feature flags
    if settings.enable_ai_chat:
        logger.info("✓ AI chat enabled")
        logger.info(f"  Model: {settings.openai_model}")
        logger.info(f"  MCP: {'enabled' if settings.enable_mcp else 'disabled'}")
        logger.info(f"  Streaming: {'enabled' if settings.ai_stream_enabled else 'disabled'}")
    else:
        logger.info("⊗ AI chat disabled")
```

---

## Docker Configuration

### Docker Compose: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # Database (Phase II - existing)
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
      POSTGRES_DB: todo_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todo_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend (Phase II + III)
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://todo_user:todo_password@db:5432/todo_db
      JWT_SECRET: ${JWT_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: ${OPENAI_MODEL:-gpt-4-turbo-preview}
      ENABLE_MCP: ${ENABLE_MCP:-true}
      ENABLE_AI_CHAT: ${ENABLE_AI_CHAT:-true}
      AI_STREAM_ENABLED: ${AI_STREAM_ENABLED:-true}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./alembic:/app/alembic
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend (Phase II + III)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      BACKEND_URL: http://backend:8000
      NEXT_PUBLIC_AI_CHAT_ENABLED: ${NEXT_PUBLIC_AI_CHAT_ENABLED:-true}
    depends_on:
      - backend
    volumes:
      - ./frontend/app:/app/app
      - ./frontend/components:/app/components
      - ./frontend/lib:/app/lib
    command: npm run dev

volumes:
  postgres_data:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
```

---

## Deployment Steps

### Local Development

```bash
# 1. Clone repository
git clone <repo-url>
cd todo-spec-driven-hackathon

# 2. Create .env file
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# 3. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. Start services with Docker Compose
docker-compose up -d

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Verify services
curl http://localhost:8000/health
curl http://localhost:8000/ai/health
curl http://localhost:3000
```

### Production Deployment

#### 1. Environment Setup

```bash
# Create production .env file
cat > .env.production << EOF
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/todo_db
JWT_SECRET=$(openssl rand -base64 32)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o  # Faster model for production
ENABLE_MCP=true
ENABLE_AI_CHAT=true
LOG_LEVEL=WARNING
EOF
```

#### 2. Build Images

```bash
# Build backend
docker build -t todo-backend:latest .

# Build frontend
docker build -t todo-frontend:latest ./frontend
```

#### 3. Deploy to Cloud

**Option A: AWS ECS**
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag todo-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest

# Deploy task definition
aws ecs update-service --cluster todo-cluster --service todo-backend --force-new-deployment
```

**Option B: Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Option C: Render**
```yaml
# render.yaml
services:
  - type: web
    name: todo-backend
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: todo-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false  # Set in dashboard

  - type: web
    name: todo-frontend
    env: docker
    dockerfilePath: ./frontend/Dockerfile
    envVars:
      - key: BACKEND_URL
        value: https://todo-backend.onrender.com

databases:
  - name: todo-db
    databaseName: todo_db
    user: todo_user
```

---

## Health Checks

### Backend Health Check

```python
# src/main.py

@app.get("/health")
async def health_check():
    """Overall application health"""
    return {
        "status": "ok",
        "version": "3.0.0",  # Phase III
        "database": "connected",
        "ai_enabled": settings.enable_ai_chat
    }

@app.get("/ai/health")
async def ai_health_check():
    """AI subsystem health"""
    # (Already defined in Phase III spec)
    pass
```

### Docker Health Checks

```yaml
# In docker-compose.yml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Monitoring & Logging

### Logging Configuration

```python
# src/config.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str):
    """Configure application logging"""
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
```

### Monitoring Endpoints

```python
# src/interfaces/monitoring.py

from fastapi import APIRouter
import psutil
import time

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

start_time = time.time()

@router.get("/metrics")
async def get_metrics():
    """Basic application metrics"""
    return {
        "uptime_seconds": time.time() - start_time,
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
```

---

## Security Considerations

### API Key Management

**DO NOT** commit `.env` files to git:

```bash
# .gitignore
.env
.env.local
.env.production
*.env
```

**DO** use secrets management in production:
- AWS Secrets Manager
- Railway environment variables
- Render environment variables

### Rate Limiting (Future)

```python
# Future enhancement
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ai/chat")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat(...):
    pass
```

---

## Backup & Recovery

### Database Backups

```bash
# Backup
docker-compose exec db pg_dump -U todo_user todo_db > backup.sql

# Restore
docker-compose exec -T db psql -U todo_user todo_db < backup.sql
```

### Automated Backups (Production)

```bash
# Cron job
0 2 * * * docker-compose exec db pg_dump -U todo_user todo_db | gzip > /backups/todo_db_$(date +\%Y\%m\%d).sql.gz
```

---

## Rollback Plan

### Version Tagging

```bash
# Tag releases
git tag -a v3.0.0 -m "Phase III: AI Chat"
git push origin v3.0.0

# Deploy specific version
docker build -t todo-backend:v3.0.0 .
```

### Rollback Procedure

```bash
# 1. Deploy previous version
docker-compose down
git checkout v2.0.0
docker-compose up -d

# 2. Rollback database if needed
docker-compose exec -T db psql -U todo_user todo_db < backup_before_v3.sql

# 3. Verify
curl http://localhost:8000/health
```

---

## Performance Tuning

### Uvicorn Workers

```bash
# Production: Use multiple workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Database Connection Pool

```python
# src/db/database.py
from sqlalchemy import create_engine

engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## Cost Optimization

### OpenAI API Costs

**GPT-4 Turbo**: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens

**Budget Calculation**:
- Average message: 200 input tokens, 400 output tokens
- Cost per message: ~$0.014
- 1000 messages/day: ~$14/day = $420/month

**Cost Reduction**:
1. Switch to `gpt-4o`: 50% cheaper
2. Implement caching for common queries
3. Add rate limiting per user

---

## Troubleshooting

### Common Issues

#### 1. OpenAI API Key Invalid

**Symptom**: `/ai/health` returns `openai_configured: false`

**Solution**:
```bash
# Check .env file
grep OPENAI_API_KEY .env

# Verify key format (should start with sk-proj-)
echo $OPENAI_API_KEY
```

#### 2. MCP Tools Not Working

**Symptom**: Agent returns errors when trying to use tools

**Solution**:
```bash
# Check MCP is enabled
grep ENABLE_MCP .env

# Check logs
docker-compose logs backend | grep MCP
```

#### 3. WebSocket Connection Failed

**Symptom**: Streaming chat doesn't work

**Solution**:
```bash
# Check WebSocket support in proxy (if using Nginx)
# Add to nginx.conf:
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## Success Criteria

✅ Backend starts with all dependencies installed
✅ Frontend builds and serves correctly
✅ Environment variables load from .env
✅ Docker Compose setup works
✅ Health checks pass
✅ Logging works correctly
✅ OpenAI API key validation works
✅ Database migrations run successfully
✅ No regressions to Phase II deployment
