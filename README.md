# Fund AI — Crowdfunding & Fundraising Platform

Fund AI is a full-stack crowdfunding and fundraising platform designed to empower individuals, communities, and non-profits to raise funds transparently for medical, educational, emergency, and social causes.

---

## 1. Project Overview
Fund AI connects donors with verified campaigners through a secure, role-based platform. Campaigners can launch fundraising projects, track collected donations in real time, and post updates. Donors can explore campaigns, save favorites, leave encouraging comments, and make secure donations with simulated payment gateways. Platform administrators oversee all operations, approve or reject pending campaigns, manage user accounts, review transactions, and audit administrative actions.

---

## 2. Features
- **Role-Based Authentication**: Secure JWT-based registration and login for Donors, Campaigners, and System Administrators.
- **Campaign Lifecycle Management**: Full workflow from creation (`PENDING`), admin review & approval/rejection (`ACTIVE` / `REJECTED`), to goal tracking (`COMPLETED`).
- **Donations & Payment Tracking**: Support for simulated payment processing with transaction references, status matrix, and goal amount aggregation.
- **Search, Filtering & Pagination**: Filter campaigns by category, title keyword search, status, and paginated record retrieval.
- **Saved Campaigns (Bookmarks)**: Donors can bookmark campaigns for quick access and tracking.
- **Interactive Comment System**: Public discussion thread on campaign pages for donor engagement.
- **User Notifications**: In-app notifications for campaign approvals, rejections, donations, and administrative actions.
- **Admin Control Center**:
  - **Overview Dashboard**: High-level platform statistics (users, campaigns, total funds raised, successful transactions).
  - **User Management**: Activate / deactivate user accounts with self-deactivation protection.
  - **Campaign Approval Portal**: Approve or reject pending campaign submissions.
  - **Audit Logging**: Immutable system audit trail capturing administrative modifications.
  - **Platform Reports & Analytics**: Real-time statistical metrics and category distribution.

---

## 3. User Roles
1. **DONOR**:
   - Browse active campaigns, filter by category/keyword.
   - Donate to active campaigns using supported payment methods.
   - View personal donation history and contribution totals.
   - Bookmark/save campaigns and write comments.
   - Receive notifications on campaign updates.
2. **CAMPAIGNER**:
   - Submit new fundraising campaigns (initial status `PENDING`).
   - Monitor created campaigns, collected funds, and donor activity.
   - Receive notifications when campaigns are approved or rejected by an admin.
3. **ADMIN**:
   - Access the dedicated Admin Control Center.
   - Approve or reject pending campaign submissions.
   - Activate or deactivate user accounts.
   - View global platform analytics, reports, transaction histories, and system audit logs.

---

## 4. Technology Stack
- **Frontend**: React 18, Vite, Vanilla CSS (Design Tokens, Glassmorphism, Micro-animations), Axios.
- **Backend**: FastAPI, Uvicorn, Python 3.10+, Pydantic v2.
- **Database**: MySQL 8.0+, SQLAlchemy ORM, PyMySQL.
- **Security**: JWT (JSON Web Tokens), Passlib (Bcrypt hashing), OAuth2 Bearer schemes, CORS middleware.

---

## 5. Architecture Overview
```
+-------------------------------------------------------+
|                React 18 + Vite Frontend                |
|       (Donor / Campaigner / Admin Control Center)     |
+-------------------------------------------------------+
                           |
                     Axios + JWT
                           v
+-------------------------------------------------------+
|                    FastAPI Backend                    |
|  - Routers: Auth, Campaigns, Donations, Admin, etc.   |
|  - Middleware: CORS, JWT Auth Bearer, Security Rules   |
+-------------------------------------------------------+
                           |
                    SQLAlchemy ORM
                           v
+-------------------------------------------------------+
|                    MySQL Database                     |
|  (users, campaigns, donations, transactions, etc.)    |
+-------------------------------------------------------+
```

---

## 6. Project Structure
```
fund/
├── backend/
│   ├── app/
│   │   ├── core/           # Database setup, security, JWT helpers
│   │   ├── models/         # SQLAlchemy ORM models (User, Campaign, Donation, etc.)
│   │   ├── routes/         # FastAPI endpoints (auth, campaigns, admin, etc.)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── main.py         # FastAPI application entrypoint & middleware
│   ├── verify_phase17.py   # Regression test suite 17
│   ├── verify_phase18.py   # Admin verification test suite 18
│   ├── verify_phase19.py   # Hardening & integration test suite 19
│   ├── verify_phase20.py   # End-to-End verification test suite 20
│   ├── .env.example        # Environment variable template
│   └── requirements.txt    # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── api.js          # Configured Axios instance with JWT interceptor
│   │   ├── App.jsx         # Main React application & role dashboard views
│   │   ├── App.css         # Custom design system & dashboard styling
│   │   └── main.jsx        # React DOM render entrypoint
│   ├── .env.example        # Frontend environment variable template
│   ├── package.json        # Frontend Node dependencies & scripts
│   └── vite.config.js      # Vite build configuration
├── .gitignore              # Repository gitignore rules
├── README.md               # Project documentation
└── DEPLOYMENT.md           # Production deployment guide
```

---

## 7. Database Setup
The application uses MySQL. Ensure MySQL server is running locally or on a managed cloud instance.

1. Create database:
```sql
CREATE DATABASE fund_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
2. Configure credentials in `backend/.env`.

Tables created automatically by SQLAlchemy ORM on backend startup:
- `users`: User profiles, roles, passwords, active status.
- `campaigns`: Fundraising projects, goal amounts, collected totals, statuses (`PENDING`, `ACTIVE`, `REJECTED`, `COMPLETED`).
- `donations`: Contribution logs, donor IDs, amounts, payment methods, transaction refs.
- `transactions`: Payment gateway ledger.
- `comments`: Campaign discussion threads.
- `saved_campaigns`: User bookmarked campaigns.
- `notifications`: User notification queue.
- `audit_logs`: Administrative audit trail.

---

## 8. Backend Setup
1. Navigate to `backend/`:
```bash
cd backend
```
2. Create and activate a Python virtual environment:
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your MySQL and JWT settings
```

---

## 9. Frontend Setup
1. Navigate to `frontend/`:
```bash
cd frontend
```
2. Install Node modules:
```bash
npm install
```
3. Configure environment:
```bash
cp .env.example .env
# Set VITE_API_URL=http://127.0.0.1:8000
```

---

## 10. Environment Variables

### Backend (`backend/.env`)
| Variable | Description | Example / Default |
|---|---|---|
| `DATABASE_URL` | MySQL Connection URL | `mysql+pymysql://root:pass@localhost:3306/fund_ai` |
| `SECRET_KEY` | JWT Secret Signing Key | `your_secret_key` |
| `ALGORITHM` | JWT Signing Algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token Expiry | `1440` |
| `CORS_ORIGINS` | Comma-separated Allowed Origins | `http://localhost:5173,http://127.0.0.1:5173` |

### Frontend (`frontend/.env`)
| Variable | Description | Example / Default |
|---|---|---|
| `VITE_API_URL` | Backend Base API URL | `http://127.0.0.1:8000` |

---

## 11. Running Locally
Start both backend and frontend development servers:

**Backend Server**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
*Backend API docs available at `http://127.0.0.1:8000/docs`*

**Frontend Dev Server**:
```bash
cd frontend
npm run dev
```
*Frontend app available at `http://localhost:5173`*

---

## 12. API Documentation Overview

| Method | Endpoint | Auth | Role | Short Description |
|---|---|---|---|---|
| `GET` | `/` | None | Public | Health Check Root |
| `POST` | `/auth/signup` | None | Public | Register donor or campaigner |
| `POST` | `/auth/login` | None | Public | Authenticate user & return JWT token |
| `GET` | `/auth/me` | JWT | Any | Get current authenticated user profile |
| `GET` | `/campaigns/` | None | Public | List active campaigns (filterable by category/search) |
| `GET` | `/campaigns/{id}` | None | Public | Get campaign details by ID |
| `POST` | `/campaigns/` | JWT | CAMPAIGNER | Submit a new campaign (`PENDING`) |
| `PUT` | `/campaigns/{id}` | JWT | CAMPAIGNER/ADMIN | Edit owned campaign |
| `DELETE` | `/campaigns/{id}` | JWT | CAMPAIGNER/ADMIN | Delete campaign |
| `POST` | `/donations/` | JWT | DONOR | Make a donation to an ACTIVE campaign |
| `GET` | `/donations/my-donations` | JWT | DONOR | Get donor's personal contribution history |
| `POST` | `/saved-campaigns/{id}` | JWT | DONOR | Bookmark/save a campaign |
| `GET` | `/saved-campaigns/` | JWT | DONOR | List donor's saved campaigns |
| `DELETE` | `/saved-campaigns/{id}` | JWT | DONOR | Remove saved campaign |
| `POST` | `/comments/` | JWT | DONOR/CAMPAIGNER/ADMIN | Post a comment on a campaign |
| `GET` | `/comments/{campaign_id}` | None | Public | Get comments for a campaign |
| `GET` | `/notifications/` | JWT | Any | Fetch user notifications |
| `PATCH` | `/notifications/{id}/read` | JWT | Any | Mark notification as read |
| `GET` | `/admin/reports` | JWT | ADMIN | Get platform reports & aggregate metrics |
| `GET` | `/admin/users` | JWT | ADMIN | List all registered users |
| `PATCH` | `/admin/users/{id}/deactivate` | JWT | ADMIN | Deactivate user account |
| `PATCH` | `/admin/campaigns/{id}/approve` | JWT | ADMIN | Approve pending campaign |
| `PATCH` | `/admin/campaigns/{id}/reject` | JWT | ADMIN | Reject pending campaign |
| `GET` | `/admin/audit-logs` | JWT | ADMIN | View system administrative audit log |

---

## 13. Testing Commands
Run test suites from the `backend/` directory:
```bash
# Run Phase 17 Core Regression Suite
python verify_phase17.py

# Run Phase 18 Admin Verification Suite
python verify_phase18.py

# Run Phase 19 Security & Integration Hardening Suite
python verify_phase19.py

# Run Phase 20 End-to-End Verification Suite
python verify_phase20.py
```

---

## 14. Production Build
Build the React frontend for production distribution:
```bash
cd frontend
npm run build
```
Production assets are generated in `frontend/dist/`.

---

## 15. Deployment Preparation & Security Notes
- **JWT Protection**: Server-side role validation enforced on all protected endpoints.
- **CORS Restricted**: Allowed origins dynamically configured via `CORS_ORIGINS`.
- **Database Safety**: Never drop production database; migrations use `Base.metadata.create_all` safely.
- **Secrets Isolation**: Real credentials kept strictly inside ignored `.env` files.

---

## 16. Known Limitations
- Payment gateways are simulated in test environments (can be integrated with Razorpay/Stripe SDKs in production).
- Email notifications require a configured SMTP provider in `.env`.