# Fund AI — Production Deployment Guide

This guide provides step-by-step instructions for deploying the **Fund AI** application to production hosting platforms (e.g. Render / Railway for Backend, Vercel / Netlify for Frontend, Managed MySQL for Database).

---

## 1. Prerequisites
- Production MySQL 8.0+ Instance (e.g. PlanetScale, AWS RDS, DigitalOcean Managed MySQL, Railway MySQL).
- Backend Hosting Account (e.g. Render, Railway, AWS App Runner, Heroku).
- Frontend Hosting Account (e.g. Vercel, Netlify, Cloudflare Pages).
- Custom Domain Name (optional) with HTTPS SSL enabled.

---

## 2. Step-by-Step Deployment Procedure

### Step 1: Provision Aiven Database (MySQL or PostgreSQL)
1. Create a database instance on **Aiven** (MySQL or PostgreSQL).
2. Get your Service URI from Aiven (e.g. `mysql://avnadmin:pass@host:port/defaultdb?ssl-mode=REQUIRED` or `postgres://...`).
   *(The backend automatically normalizes `mysql://` to `mysql+pymysql://` and `postgres://` to `postgresql://`).*

---

### Step 2: Deploy FastAPI Backend (Render)
1. Create a Web Service on Render and select the `backend/` directory as root directory.
2. Configure Build & Start Commands:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set Environment Variables in Render Backend Dashboard:
   - `DATABASE_URL`: Your Aiven database URI (e.g. `mysql+pymysql://avnadmin:...@...aivencloud.com:12345/defaultdb?ssl_mode=REQUIRED`)
   - `SECRET_KEY`: A secure random string (e.g., generated via `openssl rand -hex 32`)
   - `CORS_ORIGINS`: `https://your-frontend-name.onrender.com` (or `*` to allow all origins)

---

### Step 3: Deploy React Frontend (Render / Vercel)
1. Create a Static Site on Render (or Vercel) with root directory `frontend/`.
2. Configure Build Settings:
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`
3. Set Environment Variables **BEFORE** building:
   - `VITE_API_URL`: `https://your-backend-name.onrender.com` *(Must be set during build time in Render environment variables so Vite embeds your backend URL).*


---

## 3. Post-Deployment Verification Checklist

- [ ] **Backend Health Endpoint**: `GET /` returns `200 OK`.
- [ ] **Database Connection**: User signup & login creates persistent records in production MySQL.
- [ ] **CORS Settings**: Frontend origin is listed in backend `CORS_ORIGINS`.
- [ ] **HTTPS Enforcement**: Both frontend and backend URLs use `https://`.
- [ ] **Donor Flow**: Registration, login, campaign listing, saving campaigns, commenting, and donation works.
- [ ] **Campaigner Flow**: Campaign creation enters `PENDING` state and shows on campaigner dashboard.
- [ ] **Admin Flow**: Admin login works, pending campaigns can be approved/rejected, user accounts can be deactivated.
- [ ] **Security Review**: No `.env` or plaintext passwords committed in source control.

---

## 4. Troubleshooting

- **CORS Error in Browser Console**:
  - Verify that your exact frontend domain (e.g. `https://fundai.vercel.app`) is included in backend `CORS_ORIGINS` without trailing slashes.
- **500 Internal Server Error on API Calls**:
  - Check backend logs for MySQL connection timeout or missing table schemas. Ensure `Base.metadata.create_all(bind=engine)` executed on backend start.
- **401 Unauthorized**:
  - Verify `SECRET_KEY` matches across backend restarts and system clock is synchronized.
