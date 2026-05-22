<div align="center">

# 🔍 JobLense

### AI-Powered Job Application Tracker

Track applications, analyze resumes with ATS scoring, get smart job
recommendations, and never miss an interview — all in one place.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.2-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini_AI-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)

</div>

---

## ✨ Features

### 📄 Resume Management
- **Upload & Parse** — Drag-and-drop PDF resume upload with automatic text extraction
- **Version History** — Maintain multiple resume versions for different job targets
- **Secure Storage** — Files stored server-side with per-user isolation

### 🤖 AI-Powered ATS Analysis
- **Quick ATS Check** — Paste a job description and resume to get instant ATS score
- **Job-Linked Analysis** — Analyze resume against a specific tracked job application
- **Detailed Reports** — Keyword match, formatting, skills gap, grammar, and top 5 recommendations
- **Powered by Gemini** — Uses Google Gemini 2.5 Flash for fast, accurate analysis

### 💼 Job Application Tracker
- **Full CRUD** — Create, view, edit, and delete job applications
- **Status Pipeline** — Track through: Saved → Applied → Interview → Offer → Rejected
- **Interview Scheduling** — Set interview dates with automated email reminders
- **Rich Details** — Store company, platform, salary, HR contact, notes, and more

### 🎯 Smart Recommendations
- **AI Job Matching** — Personalized job role suggestions based on your resume
- **Background Processing** — Generated asynchronously so UI stays responsive

### 🔐 Authentication
- **Email and Password** — JWT tokens stored in secure httpOnly cookies
- **Google OAuth** — One-click sign-in with Google via OAuth 2.0
- **Facebook OAuth** — One-click sign-in with Facebook via OAuth 2.0
- **Session Management** — Secure session middleware with CSRF protection

### 📧 Email Notifications
- **Interview Reminders** — Automatic email alerts on interview day at 8 AM
- **Scheduled Jobs** — APScheduler runs background cron jobs for timely notifications

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, React Router v6, TanStack React Query |
| Backend | FastAPI, Uvicorn, SQLAlchemy async, Pydantic v2 |
| Primary DB | MySQL 8 (structured data — users, jobs, resumes) |
| Secondary DB | MongoDB Atlas (AI reports and recommendations) |
| AI | Google Gemini 2.5 Flash |
| Auth | JWT httpOnly cookie, Google OAuth 2.0, Facebook OAuth 2.0 |
| Email | FastAPI-Mail, Gmail SMTP with App Passwords |
| Scheduler | APScheduler (Windows friendly, no Redis needed) |
| UI Icons | Lucide React |

---

## 📁 Project Structure

    JobLense/
    ├── backend/
    │   ├── app/
    │   │   ├── api/v1/
    │   │   │   ├── auth.py                 Login, register, OAuth flows
    │   │   │   ├── resume.py               Resume upload and retrieval
    │   │   │   ├── ats.py                  ATS analysis endpoints (2 flows)
    │   │   │   ├── jobs.py                 Job CRUD operations
    │   │   │   └── recommendations.py      AI job recommendations
    │   │   ├── core/
    │   │   │   ├── config.py               Pydantic settings from .env
    │   │   │   ├── security.py             JWT token creation and validation
    │   │   │   ├── oauth.py                Google and Facebook OAuth setup
    │   │   │   ├── dependencies.py         FastAPI dependency injection
    │   │   │   └── scheduler.py            APScheduler configuration
    │   │   ├── db/
    │   │   │   ├── models/                 SQLAlchemy ORM models
    │   │   │   ├── mysql.py                Async SQLAlchemy engine and session
    │   │   │   └── mongodb.py              Motor async MongoDB client
    │   │   ├── schemas/                    Pydantic request and response schemas
    │   │   ├── services/
    │   │   │   ├── ats_service.py          ATS scoring with Gemini AI
    │   │   │   ├── auth_service.py         User registration and login logic
    │   │   │   ├── job_service.py          Job application CRUD logic
    │   │   │   ├── resume_service.py       Resume file handling and PDF parsing
    │   │   │   ├── recommendation_service.py   AI recommendations
    │   │   │   ├── email_service.py        Email sending via SMTP
    │   │   │   └── gemini_utils.py         Shared Gemini utility functions
    │   │   └── tasks/
    │   │       └── interview_reminder.py   Scheduled reminder cron job
    │   ├── alembic/                        Database migrations
    │   ├── uploads/                        Uploaded resume files
    │   ├── requirements.txt
    │   ├── OAUTH_SETUP.md
    │   └── .env.example
    │
    └── frontend/
        ├── src/
        │   ├── api/                        Axios API client files
        │   ├── components/
        │   │   ├── layout/                 Navbar, sidebar, page layout
        │   │   ├── shared/                 Reusable components
        │   │   └── ui/                     Buttons, spinners, inputs
        │   ├── context/                    React context AuthContext
        │   ├── hooks/                      Custom React hooks
        │   ├── pages/
        │   │   ├── Auth/                   Login, Register, OAuthCallback
        │   │   ├── Dashboard/              Main dashboard with stats
        │   │   ├── Resume/                 Upload and list resumes
        │   │   ├── ATS/                    Quick check and detailed reports
        │   │   ├── Jobs/                   Job list, create, edit, detail
        │   │   └── Recommendations/        AI powered job suggestions
        │   ├── utils/                      Utility functions and constants
        │   ├── App.jsx                     Root routing component
        │   └── main.jsx                    React entry point
        ├── index.html
        ├── vite.config.js
        ├── tailwind.config.js
        └── package.json

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- MySQL 8
- MongoDB Atlas account
- Google Gemini API key
- Google and Facebook OAuth credentials

### 1. Clone the Repository

    git clone https://github.com/shivam697/Joblens.git
    cd Joblens

### 2. Backend Setup

    cd backend
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # macOS and Linux
    source venv/bin/activate

    pip install -r requirements.txt

#### Configure Environment Variables

    cp .env.example .env

Open `backend/.env` and fill in all required values.

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Random 32+ character string for JWT signing |
| `MYSQL_HOST` | ✅ | MySQL host (localhost for local) |
| `MYSQL_DATABASE` | ✅ | Database name (joblense) |
| `MYSQL_USER` | ✅ | MySQL username |
| `MYSQL_PASSWORD` | ✅ | MySQL password |
| `MONGODB_URI` | ✅ | MongoDB Atlas connection string |
| `GOOGLE_CLIENT_ID` | ✅ | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | ✅ | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | ✅ | http://localhost:8000/api/v1/auth/google/callback |
| `FACEBOOK_CLIENT_ID` | ✅ | From Facebook Developers |
| `FACEBOOK_CLIENT_SECRET` | ✅ | From Facebook Developers |
| `GEMINI_API_KEY` | ✅ | From Google AI Studio |
| `MAIL_USERNAME` | ✅ | Gmail address for notifications |
| `MAIL_PASSWORD` | ✅ | Gmail App Password 16 characters |
| `FRONTEND_URL` | ✅ | http://localhost:5173 |

#### Run Database Migrations

    alembic upgrade head

#### Start Backend Server

    uvicorn app.main:app --host localhost --port 8000 --reload

API available at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

### 3. Frontend Setup

    cd frontend
    npm install
    npm run dev

Frontend available at **http://localhost:5173**

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register a new user |
| POST | /api/v1/auth/login | Login with email and password |
| POST | /api/v1/auth/logout | Logout and clear cookie |
| GET | /api/v1/auth/me | Get current user profile |
| GET | /api/v1/auth/google/login | Initiate Google OAuth |
| GET | /api/v1/auth/google/callback | Google OAuth callback |
| GET | /api/v1/auth/facebook/login | Initiate Facebook OAuth |
| GET | /api/v1/auth/facebook/callback | Facebook OAuth callback |
| POST | /api/v1/resume/upload | Upload a resume PDF or text |
| GET | /api/v1/resume/ | List user resumes |
| PATCH | /api/v1/resume/{id}/activate | Set resume as active |
| DELETE | /api/v1/resume/{id} | Delete a resume |
| POST | /api/v1/ats/quick-analyze | Flow 1 quick ATS check |
| POST | /api/v1/ats/analyze | Flow 2 job-linked ATS analysis |
| GET | /api/v1/ats/report/{id} | Poll ATS report by ID |
| GET | /api/v1/ats/history | Get ATS analysis history |
| GET | /api/v1/jobs/ | List all job applications |
| POST | /api/v1/jobs/ | Create a job application |
| GET | /api/v1/jobs/stats | Get dashboard stats |
| GET | /api/v1/jobs/{id} | Get job application details |
| PUT | /api/v1/jobs/{id} | Update a job application |
| DELETE | /api/v1/jobs/{id} | Soft delete a job application |
| POST | /api/v1/recommendations/ | Generate AI recommendations |
| GET | /api/v1/recommendations/ | Get saved recommendations |
| GET | /health | Health check |

---

## 📸 ATS Analysis — Two Flows

**Flow 1 — Quick Check** (no job tracking needed)

    Upload resume PDF or text
            ↓
    Paste any job description
            ↓
    Click Analyze Now
            ↓
    Gemini 2.5 Flash analyzes in background
            ↓
    Full report: score, keywords, grammar, recommendations

**Flow 2 — Job Linked** (tied to a tracked job)

    Create job application with job description
            ↓
    Link your resume to that job
            ↓
    Click Analyze with AI on job detail page
            ↓
    Report permanently saved against that company
            ↓
    Revisit anytime to track improvement

---

## 🛠️ Development

### Running Both Servers

Open two terminals:

    # Terminal 1 — Backend
    cd backend
    venv\Scripts\activate
    uvicorn app.main:app --reload --port 8000

    # Terminal 2 — Frontend
    cd frontend
    npm run dev

### Database Migrations

    cd backend
    alembic revision --autogenerate -m "description"
    alembic upgrade head

### Build Frontend for Production

    cd frontend
    npm run build

---

## 🔑 OAuth Setup

See [OAUTH_SETUP.md](./backend/OAUTH_SETUP.md) for complete step by step
Google OAuth and Facebook OAuth configuration instructions.

---


---

<div align="center">

**Built with ❤️ using FastAPI + React + Gemini AI**

</div>