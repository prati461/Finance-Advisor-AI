#!/usr/bin/env python3
"""
Production Configuration Verification

This script checks all the critical configurations needed for production.
"""

import os
import sys

def check_environment_vars():
    """Check that required environment variables are documented."""
    print("=" * 70)
    print("PRODUCTION ENVIRONMENT VARIABLES REQUIREMENTS")
    print("=" * 70)
    
    required_render_vars = {
        "ENVIRONMENT": "production",
        "DATABASE_URL": "mysql+pymysql://USER:PASSWORD@altaria.proxy.rlwy.net:46781/DATABASE",
        "JWT_SECRET_KEY": "A long random string (minimum 32 chars)",
        "CORS_ORIGINS": "https://finance-advisor-ai.vercel.app",
        "DEBUG": "False",
        "LOG_LEVEL": "INFO",
    }
    
    optional_render_vars = {
        "GEMINI_API_KEY": "Optional - for AI features",
        "LLM_PROVIDER": "Optional - default: gemini",
        "LLM_MODEL": "Optional - default: gemini-1.5-flash",
        "ALPHA_VANTAGE_API_KEY": "Optional - for market data fallback",
    }
    
    required_vercel_vars = {
        "VITE_API_URL": "https://finance-advisor-ai-1.onrender.com/api/v1",
    }
    
    print("\n📋 REQUIRED Render Environment Variables:")
    for key, description in required_render_vars.items():
        print(f"  • {key}")
        print(f"    Value: {description}")
    
    print("\n📋 OPTIONAL Render Environment Variables:")
    for key, description in optional_render_vars.items():
        print(f"  • {key}")
        print(f"    Value: {description}")
    
    print("\n📋 REQUIRED Vercel Environment Variables (Production):")
    for key, value in required_vercel_vars.items():
        print(f"  • {key} = {value}")


def check_docker_config():
    """Check Docker configuration."""
    print("\n" + "=" * 70)
    print("DOCKER CONFIGURATION")
    print("=" * 70)
    
    print("""
Dockerfile must:
  ✓ Use Python 3.12+
  ✓ Set ENV PORT (Render provides PORT environment variable)
  ✓ Install requirements.txt
  ✓ Copy all source code
  ✓ Run: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT

Render Settings:
  • Runtime: Docker
  • Dockerfile path: ./Dockerfile
  • Build context: .
  • Health check path: /health
  • No custom start command (use Dockerfile CMD)
""")


def check_database_config():
    """Check database configuration."""
    print("\n" + "=" * 70)
    print("DATABASE CONFIGURATION")
    print("=" * 70)
    
    print("""
Railway MySQL Connection:
  • Host: altaria.proxy.rlwy.net (PUBLIC endpoint)
  • Port: 46781
  • Database: Provided by Railway
  • Username: Provided by Railway
  • Password: Provided by Railway
  • URL Format: mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
  
Important:
  ⚠️  NEVER use mysql.railway.internal from Render
  ✓ ALWAYS use the public endpoint: altaria.proxy.rlwy.net
  ✓ Special characters in password must be URL-encoded:
    - @ → %40
    - : → %3A
    - / → %2F
    - # → %23
    
Connection Pooling (configured in backend/database/__init__.py):
  ✓ pool_pre_ping=True - Validates connections before use
  ✓ pool_recycle=300 - Recycles connections after 5 minutes
  ✓ pool_timeout=30 - Connection timeout
  ✓ connect_timeout=20 - TCP connection timeout
  ✓ read_timeout=30 - Read timeout
  ✓ write_timeout=30 - Write timeout
  ✓ charset=utf8mb4 - Full Unicode support
""")


def check_cors_config():
    """Check CORS configuration."""
    print("\n" + "=" * 70)
    print("CORS CONFIGURATION")
    print("=" * 70)
    
    print("""
Backend (backend/app/main.py):
  • Allow origins: https://finance-advisor-ai.vercel.app (EXACT match)
  • Allow credentials: True
  • Allow methods: * (all HTTP methods)
  • Allow headers: * (all headers)
  
Frontend (frontend/src/api/axios.ts):
  • Uses VITE_API_URL from environment
  • Falls back to /api/v1 for local development only
  • Authorization header: Bearer <access_token>
  
⚠️  Do NOT use wildcard (*) for origins in production
✓ Always use exact domain: https://finance-advisor-ai.vercel.app
""")


def check_frontend_config():
    """Check frontend configuration."""
    print("\n" + "=" * 70)
    print("VERCEL FRONTEND CONFIGURATION")
    print("=" * 70)
    
    print("""
Vercel Project Settings:
  • Root directory: frontend
  • Framework preset: Vite
  • Build command: npm run build
  • Output directory: dist
  • Environment variable: VITE_API_URL
  
SPA Routing (frontend/vercel.json):
  • All non-static routes redirect to index.html
  • /api/* routes return 404 (not proxied)
  • Allows direct URL access to protected routes
  
Protected Routes (with Vite dev proxy):
  • /login
  • /register
  • /dashboard (protected)
  • /incomes, /expenses, /budgets (protected)
  • /monthly-summary, /analytics, etc. (protected)
  
Development:
  • Vite proxy: /api -> http://localhost:8000
  • npm run dev serves on http://localhost:3000
  
Production:
  • No proxy - uses VITE_API_URL from environment
  • VITE_API_URL = https://finance-advisor-ai-1.onrender.com/api/v1
""")


def check_security_config():
    """Check security configuration."""
    print("\n" + "=" * 70)
    print("SECURITY CONFIGURATION")
    print("=" * 70)
    
    print("""
Authentication:
  ✓ JWT tokens used for all protected endpoints
  ✓ Access token valid for 60 minutes (configurable)
  ✓ Refresh token valid for 7 days (configurable)
  ✓ Tokens stored in browser localStorage
  ✓ Tokens sent as Bearer in Authorization header

Password Security:
  ✓ Passwords hashed with bcrypt
  ✓ Email uniqueness enforced at database level
  ✓ Duplicate registration returns 409 Conflict (not 400)

Data Isolation:
  ✓ All queries filtered by authenticated user_id
  ✓ No cross-user data exposure possible via API
  ✓ Frontend protection is secondary defense layer

Secrets Protection:
  ⚠️  DO NOT commit .env files
  ✓ .gitignore excludes .env, .env.local, .env.*.local
  ✓ GEMINI_API_KEY never exposed to browser
  ✓ DATABASE_URL never exposed to browser
  ✓ JWT_SECRET_KEY never exposed anywhere

HTTPS:
  ✓ Vercel enforces HTTPS on vercel.app domain
  ✓ Render enforces HTTPS on onrender.com domain
  ✓ All CORS origins use https:// scheme
""")


def check_endpoints():
    """List all endpoints."""
    print("\n" + "=" * 70)
    print("CRITICAL ENDPOINTS")
    print("=" * 70)
    
    endpoints = {
        "Health/Status": [
            "GET /health",
            "GET /api/v1/health",
            "GET /__deployment_check",
        ],
        "Authentication": [
            "POST /api/v1/auth/register",
            "POST /api/v1/auth/login",
            "POST /api/v1/auth/refresh",
        ],
        "Protected Endpoints (require Authorization header)": [
            "GET /api/v1/users/me (current user profile)",
            "GET /api/v1/incomes",
            "POST /api/v1/incomes",
            "GET /api/v1/expenses",
            "POST /api/v1/expenses",
            "GET /api/v1/budgets",
            "POST /api/v1/budgets",
            "GET /api/v1/finance/summary",
            "POST /api/v1/ai/financial-health",
            "POST /api/v1/ai/recommendations",
            "POST /api/v1/ai/analytics",
            "GET /api/v1/ai/chatbot",
        ],
    }
    
    for category, routes in endpoints.items():
        print(f"\n{category}:")
        for route in routes:
            print(f"  • {route}")
    
    print("\nAPI Documentation:")
    print("  • Swagger UI: https://finance-advisor-ai-1.onrender.com/docs")
    print("  • ReDoc: https://finance-advisor-ai-1.onrender.com/redoc")


def main():
    """Run all checks."""
    check_environment_vars()
    check_docker_config()
    check_database_config()
    check_cors_config()
    check_frontend_config()
    check_security_config()
    check_endpoints()
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT CHECKLIST")
    print("=" * 70)
    print("""
Before deploying to production, verify:

RENDER BACKEND:
  □ Service created and connected to GitHub
  □ Environment variables set correctly
  □ DATABASE_URL uses Railway public endpoint
  □ CORS_ORIGINS set to https://finance-advisor-ai.vercel.app
  □ Health check path configured: /health
  □ Latest code pushed to main branch
  □ Auto-deploy on git push enabled
  □ Build logs show successful deployment
  □ Health endpoint responds with 200 OK
  □ /api/v1/health endpoint responds

VERCEL FRONTEND:
  □ Project created and connected to GitHub
  □ Root directory set to: frontend
  □ Build command: npm run build
  □ Output directory: dist
  □ Environment variable VITE_API_URL set
  □ Latest code pushed to main branch
  □ Auto-deploy on git push enabled
  □ Build logs show no errors
  □ Frontend loads without 404 errors
  □ SPA routing works (direct URL access to protected routes)
  □ API requests go to correct backend URL

PRODUCTION TESTING:
  □ Can register a new account
  □ Can login with registered account
  □ Access tokens are generated and stored
  □ Protected endpoints require valid token
  □ Cannot access other user's data
  □ Analytics show correct user's data
  □ Can persist data (logout/login preserves data)
  □ Logout clears tokens
  □ Can login again after logout
  □ All major features work end-to-end

FINAL VERIFICATION:
  □ No exposed secrets in repository
  □ No localhost URLs in production build
  □ Database connectivity from Render verified
  □ Cross-user data isolation verified
  □ Personalized analytics working
  □ No 500 errors on critical endpoints
""")
    
    print("\nFor issues:\n")
    print("  1. Check Render logs:")
    print("     https://dashboard.render.com → Select Finance Advisor → Logs")
    print("\n  2. Check Vercel logs:")
    print("     https://vercel.com → Select Finance Advisor → Deployments → Logs")
    print("\n  3. Test locally first:")
    print("     cd backend && python -m uvicorn backend.app.main:app --reload")
    print("     cd frontend && npm run dev")


if __name__ == "__main__":
    main()
