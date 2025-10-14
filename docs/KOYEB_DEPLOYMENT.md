# 🚀 Koyeb Deployment Guide - AreaMédica API

Complete guide to deploy AreaMédica API on Koyeb's free tier.

## 📋 Prerequisites

- [x] GitHub account
- [x] Koyeb account (free, no credit card): https://app.koyeb.com/auth/signup
- [x] Neon PostgreSQL account (free): https://console.neon.tech/signup

---

## 🗄️ Step 1: Create PostgreSQL Database (Neon)

Koyeb doesn't provide managed PostgreSQL in the free tier, so we'll use Neon (also free).

### 1.1 Sign up for Neon
1. Go to https://neon.tech
2. Click **"Sign Up"** (GitHub sign-in recommended)
3. Verify your email

### 1.2 Create Database
1. Click **"Create Project"**
2. Project settings:
   - **Name**: `areamedica-db`
   - **PostgreSQL Version**: `16` (latest)
   - **Region**: `US East (Ohio)` or closest to Washington DC
3. Click **"Create Project"**

### 1.3 Get Connection String
1. In your Neon dashboard, click on **"Connection Details"**
2. Select **"Pooled connection"** (recommended for serverless)
3. Copy the connection string (format: `postgresql://user:password@host/dbname?sslmode=require`)
4. **Save this** - you'll need it in Step 3

**Example:**
```
postgresql://areamedica_user:AbCd1234XyZ@ep-cool-forest-123456.us-east-2.aws.neon.tech/areamedica?sslmode=require
```

---

## 🔐 Step 2: Generate SECRET_KEY

You need a secure secret key for JWT tokens.

### Option A: Python (Recommended)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Option B: OpenSSL
```bash
openssl rand -base64 32
```

**Save this key** - you'll use it in Step 3.

---

## 🚀 Step 3: Deploy to Koyeb

### 3.1 Connect GitHub Repository

1. Go to https://app.koyeb.com
2. Click **"Create App"**
3. Select **"GitHub"** as deployment method
4. Click **"Connect to GitHub"**
5. Authorize Koyeb to access your repository
6. Select repository: **`niokistudio/areamedica-api`**
7. Select branch: **`main`**

### 3.2 Configure Service

**Builder**: Select **"Docker"**

**Dockerfile path**: `docker/Dockerfile`

**Port**: `8000`

**Health check path**: `/health`

### 3.3 Set Environment Variables

Click **"Advanced"** → **"Environment Variables"**

**Required Secrets** (click "Add Secret"):

| Variable | Type | Value |
|----------|------|-------|
| `SECRET_KEY` | Secret | Your generated secret key from Step 2 |
| `DATABASE_URL` | Secret | Your Neon connection string from Step 1.3 |
| `BANESCO_API_KEY` | Secret | `test-api-key-12345` (fake for testing) |
| `BANESCO_PASSWORD` | Secret | `test-password` (fake for testing) |

**Public Environment Variables** (click "Add Environment Variable"):

| Variable | Value | Description |
|----------|-------|-------------|
| `ENVIRONMENT` | `production` | Running environment |
| `DEBUG` | `false` | Disable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `8000` | Application port |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration |
| `CORS_ORIGINS` | `*` | CORS allowed origins (change to your frontend domain) |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials |
| `CORS_ALLOW_METHODS` | `GET,POST,PUT,DELETE,PATCH,OPTIONS` | HTTP methods |
| `CORS_ALLOW_HEADERS` | `*` | Allowed headers |
| `BANESCO_BASE_URL` | `https://fake-api.banesco.com` | Fake API for testing |
| `BANESCO_USERNAME` | `test-user` | Fake username |
| `BANESCO_TIMEOUT` | `30` | API timeout |
| `RATE_LIMIT_ENABLED` | `false` | Disable Redis-based rate limiting |
| `ENABLE_METRICS` | `true` | Enable metrics |

### 3.4 Deploy

1. Review all settings
2. Click **"Deploy"**
3. Wait 3-5 minutes for deployment

---

## ✅ Step 4: Verify Deployment

### 4.1 Check Health

Once deployed, Koyeb will give you a URL like:
```
https://areamedica-api-yourname.koyeb.app
```

Test the health endpoint:
```bash
curl https://areamedica-api-yourname.koyeb.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-10-12T20:00:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

### 4.2 Test Authentication

Login with default admin user:
```bash
curl -X POST https://areamedica-api-yourname.koyeb.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@areamedica.com",
    "password": "Admin123!"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid-here",
    "email": "admin@areamedica.com",
    "full_name": "Administrador",
    "role": "ADMIN"
  }
}
```

### 4.3 Test Protected Endpoint

Use the token from step 4.2:
```bash
TOKEN="your-token-here"

curl https://areamedica-api-yourname.koyeb.app/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Step 5: Monitor Logs

### View Deployment Logs
1. Go to Koyeb dashboard
2. Click on **"areamedica-api"** service
3. Click **"Logs"** tab

Look for:
```
==> Starting AreaMédica API...
==> Port: 8000
==> Running database migrations...
INFO  [alembic.runtime.migration] Running upgrade -> eceff2145126, initial schema
==> Starting uvicorn server...
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🎯 Default Test Users

After migrations run, these users are available:

| Email | Password | Role | Permissions |
|-------|----------|------|-------------|
| `admin@areamedica.com` | `Admin123!` | ADMIN | All permissions |
| `usuario@areamedica.com` | `User123!` | USER | Read/create transactions |
| `test@areamedica.com` | `Test123!` | USER | Read-only |

---

## 🔧 Troubleshooting

### Database Connection Issues

**Error**: `could not connect to server`

**Solution**:
1. Verify your Neon database is active
2. Check `DATABASE_URL` format:
   ```
   postgresql://user:password@host.neon.tech/dbname?sslmode=require
   ```
3. Ensure you're using **Pooled connection** string from Neon

### Migrations Not Running

**Error**: `relation "users" does not exist`

**Solution**:
1. Check Koyeb logs for migration errors
2. Manually run migrations:
   - Go to Koyeb **"Shell"** tab
   - Run: `alembic upgrade head`

### Health Check Failing

**Error**: Health check returns 503 or times out

**Solution**:
1. Check if database connection is working
2. Verify `PORT` environment variable is `8000`
3. Check logs for startup errors

### Token Errors

**Error**: `Could not validate credentials`

**Solution**:
1. Verify `SECRET_KEY` is set correctly
2. Ensure `ALGORITHM` is `HS256`
3. Check token hasn't expired

---

## 📊 Free Tier Limits

Koyeb Free Tier includes:

- ✅ **Compute**: 512 MB RAM, 0.1 vCPU
- ✅ **Storage**: 2 GB disk space
- ✅ **Bandwidth**: Unlimited
- ✅ **Instances**: 2 free services
- ✅ **SSL**: Automatic HTTPS
- ✅ **Custom domains**: Supported
- ✅ **Always on**: No sleep/hibernation

Neon Free Tier includes:

- ✅ **Storage**: 3 GB
- ✅ **Compute**: 0.25 vCPU
- ✅ **Active time**: 100 hours/month (auto-suspend after 5 min inactivity)
- ✅ **Branches**: 10 project branches

---

## 🔄 Auto-Deployment

Koyeb automatically redeploys when you push to `main` branch:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Koyeb detects push and redeploys automatically
```

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain

1. Go to Koyeb dashboard
2. Click **"Domains"**
3. Click **"Add Domain"**
4. Enter your domain: `api.areamedica.com`
5. Add DNS records to your domain provider:
   ```
   Type: CNAME
   Name: api
   Value: areamedica-api-yourname.koyeb.app
   ```

---

## 📈 Next Steps

### Production Readiness

1. **Update CORS Origins**:
   ```
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

2. **Set Real Banesco Credentials**:
   - Update `BANESCO_BASE_URL`
   - Update `BANESCO_API_KEY`
   - Update `BANESCO_USERNAME`
   - Update `BANESCO_PASSWORD`

3. **Enable Rate Limiting** (requires Redis):
   - Add Redis (external service like Upstash)
   - Set `REDIS_URL`
   - Set `RATE_LIMIT_ENABLED=true`

4. **Monitor Performance**:
   - Use Koyeb metrics dashboard
   - Set up alerts for errors
   - Monitor database usage in Neon

---

## 💰 Cost Estimates

| Tier | Koyeb | Neon PostgreSQL | Total |
|------|-------|-----------------|-------|
| **Free** | $0 | $0 | **$0/month** |
| **Paid** | $5.40/mo | $19/mo | $24.40/mo |

**Recommendation**: Start with free tier for MVP/testing, upgrade when needed.

---

## 📚 Additional Resources

- [Koyeb Documentation](https://www.koyeb.com/docs)
- [Neon Documentation](https://neon.tech/docs/introduction)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [API Documentation](./API_DOCUMENTATION.md)

---

## 🆘 Support

- **Koyeb Support**: https://www.koyeb.com/docs/help/support
- **Neon Community**: https://community.neon.tech
- **Project Issues**: https://github.com/niokistudio/areamedica-api/issues

---

**Last Updated**: October 12, 2024
**Version**: 1.0.0
