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

### Step 1: Deploy Managed MySQL Database
1. Provision a MySQL database instance.
2. Create the production database:
```sql
CREATE DATABASE fund_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
3. Copy the database connection URL:
```
mysql+pymysql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/fund_ai
```
*(Do NOT commit this connection URL to Git).*

---

### Step 2: Deploy FastAPI Backend (Render / Railway)
1. Connect your repository to Render/Railway and select the `backend/` directory as root.
2. Set Environment Variables in your hosting dashboard:
   - `DATABASE_URL`: Your managed MySQL connection URL.
   - `SECRET_KEY`: A secure random 64-character string.
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `1440`
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app`
3. Configure Build & Start Commands:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Deploy the backend service.
5. Verify health check by visiting:
   ```
   GET https://your-backend-domain.onrender.com/
   ```
   Should return: `{"message": "Fund AI Backend is running", "status": "success"}`

---

### Step 3: Deploy React Frontend (Vercel / Netlify)
1. Import the repository into Vercel/Netlify.
2. Set the Root Directory to `frontend/`.
3. Set Build Settings:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Set Environment Variables:
   - `VITE_API_URL`: `https://your-backend-domain.onrender.com`
5. Deploy the site.

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
