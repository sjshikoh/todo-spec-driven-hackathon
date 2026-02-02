# Deployment Guide

This guide details how to deploy the Todo Application to production.

## Project Overview

- **Frontend**: Next.js 14 with Better Auth, TailwindCSS
- **Backend**: FastAPI Python server with SQLModel
- **Database**: Neon PostgreSQL (serverless)
- **Authentication**: Better Auth with JWT/JWKS

## Prerequisites

1. **Accounts Required**:
   - GitHub/GitLab (source code)
   - Neon.tech (PostgreSQL database)
   - Deployment platform (Vercel, Railway, AWS, etc.)

2. **Tools Required**:
   - Docker & Docker Compose (for containerization)
   - Git
   - Node.js 18+ (frontend)
   - Python 3.10+ (backend)

## Security Checklist

✅ **Before deploying to production**:

- [ ] Remove all hardcoded credentials from `.env`
- [ ] Add `.env` to `.gitignore` (already done)
- [ ] Use `.env.example` as template
- [ ] Rotate Neon database credentials
- [ ] Update CORS origins to production URLs
- [ ] Remove localhost URLs from configuration

## Environment Variables

### Backend (FastAPI)
Create `.env` file in project root:

```env
# Database Configuration (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@ep-example.neon.tech/neondb?sslmode=require

# Auth Configuration
BETTER_AUTH_URL=https://your-frontend-domain.com

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Origins (comma separated)
ALLOWED_ORIGINS=https://your-frontend-domain.com

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Optional: JWT Configuration (if using custom JWT)
# JWT_SECRET_KEY=your-secret-key-here
# JWT_ALGORITHM=HS256
```

### Frontend (Next.js)
Create `.env.local` in `/frontend`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://your-backend-domain.com

# Better Auth Configuration
DATABASE_URL=postgresql://auth_user:auth_password@auth-db-host:5432/auth_db
NEXTAUTH_URL=https://your-frontend-domain.com
NEXTAUTH_SECRET=your-nextauth-secret
```

## Deployment Options

### Option 1: Docker Compose (Simplest)

1. **Update `docker-compose.yml`** for production:
   ```yaml
   # Change database service to use Neon
   environment:
     DATABASE_URL: ${DATABASE_URL}
     BETTER_AUTH_URL: ${BETTER_AUTH_URL}
   ```

2. **Build and deploy**:
   ```bash
   # Build images
   docker-compose build

   # Run in production mode
   docker-compose up -d
   ```

### Option 2: Vercel + Railway (Recommended)

#### Frontend (Vercel):
1. Connect GitHub repository to Vercel
2. Set root directory to `/frontend`
3. Configure environment variables
4. Deploy automatically on push to main

#### Backend (Railway):
1. Create new project on Railway
2. Connect GitHub repository
3. Add **PostgreSQL** database
4. Configure environment variables
5. Set start command: `python src/main.py`
6. Deploy

### Option 3: AWS/Azure/GCP

#### Using Docker:
1. **Build images**:
   ```bash
   docker build -f Dockerfile.backend -t todo-backend .
   docker build -f Dockerfile.frontend -t todo-frontend .
   ```

2. **Push to container registry**:
   ```bash
   docker tag todo-backend your-registry/todo-backend:latest
   docker push your-registry/todo-backend:latest
   ```

3. **Deploy to**:
   - AWS ECS/EKS
   - Google Cloud Run
   - Azure Container Apps

## Database Setup

### Neon PostgreSQL:
1. Create new project on Neon.tech
2. Copy connection string
3. Test connection:
   ```bash
   psql "postgresql://username:password@ep-example.neon.tech/neondb?sslmode=require"
   ```

### Migrations:
The application uses SQLModel's `create_all()` for table creation. For production:

1. **Manual migration**:
   ```python
   from src.db.database import engine
   from src.models.task import Task
   Task.metadata.create_all(engine)
   ```

2. **Recommended**: Add Alembic for proper migrations

## Monitoring & Health Checks

### Backend Health Check:
```bash
curl https://your-backend-domain.com/
# Should return: {"message": "Todo API is running"}
```

### Frontend Health Check:
```bash
curl -I https://your-frontend-domain.com/
# Should return HTTP 200
```

## Troubleshooting

### Common Issues:

1. **CORS errors**:
   - Check `ALLOWED_ORIGINS` includes frontend URL
   - Ensure no trailing slashes in URLs

2. **Database connection**:
   - Verify Neon connection string
   - Check firewall/network access

3. **Authentication failures**:
   - Verify `BETTER_AUTH_URL` points to frontend
   - Check JWT token validation

### Logs:
```bash
# Docker logs
docker-compose logs backend
docker-compose logs frontend

# Railway logs
railway logs

# Vercel logs
vercel logs
```

## Maintenance

### Updates:
1. Pull latest changes
2. Rebuild Docker images
3. Deploy with zero-downtime strategy

### Backups:
1. Neon provides automatic backups
2. Export data: `pg_dump`
3. Regular snapshot of production database

## Security Best Practices

1. **Never commit credentials**
2. **Use different databases** for development/production
3. **Enable HTTPS** everywhere
4. **Regular security updates**
5. **Monitor access logs**
6. **Implement rate limiting** (consider adding to backend)
7. **Use secret managers** (AWS Secrets Manager, HashiCorp Vault)

## Support

For issues:
1. Check logs
2. Verify environment variables
3. Test locally with Docker Compose
4. Review deployment platform documentation