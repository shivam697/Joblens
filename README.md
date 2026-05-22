<![CDATA[<div align="center">

# 🔍 JobLense

### AI-Powered Job Application Tracker

Track applications, analyze resumes with ATS scoring, get smart job recommendations, and never miss an interview — all in one place.

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
- **Upload & Parse** — Drag-and-drop PDF resume upload with automatic text extraction using `pdfplumber`
- **Version History** — Maintain multiple resume versions for different job targets
- **Secure Storage** — Files stored server-side with per-user isolation

### 🤖 AI-Powered ATS Analysis
- **Quick ATS Check** — Paste a job description and your resume to get an instant ATS compatibility score
- **Detailed Reports** — Section-by-section breakdown including keyword match, formatting, skills gap, and actionable improvement suggestions
- **Powered by Gemini** — Uses Google's Gemini 2.5 Flash model for fast, accurate analysis

### 💼 Job Application Tracker
- **Full CRUD** — Create, view, edit, and delete job applications
- **Status Pipeline** — Track applications through stages: Applied → Interview → Offer → Rejected
- **Interview Scheduling** — Set interview dates with automated email reminders
- **Rich Details** — Store company, role, salary, location, notes, and more

### 🎯 Smart Recommendations
- **AI Job Matching** — Get personalized job recommendations based on your resume and preferences
- **Background Processing** — Recommendations are generated asynchronously so the UI stays responsive

### 🔐 Authentication
- **Email/Password** — Traditional registration and login with secure JWT tokens stored in httpOnly cookies
- **Google OAuth** — One-click sign-in with Google via OAuth 2.0
- **Session Management** — Secure session middleware with CSRF protection

### 📧 Email Notifications
- **Interview Reminders** — Automatic email alerts before upcoming interviews
- **Scheduled Jobs** — APScheduler runs background cron jobs for timely notifications

---

## 🏗️ Tech Stack

| Layer        | Technology                                                         |
| ------------ | ------------------------------------------------------------------ |
| **Frontend** | React 18, Vite, TailwindCSS, React Router v6, TanStack React Query |
| **Backend**  | FastAPI, Uvicorn, SQLAlchemy (async), Pydantic v2                  |
| **Database** | SQLite (dev) / MySQL (prod), MongoDB (job tracking & documents)    |
| **AI**       | Google Gemini 2.5 Flash                                            |
| **Auth**     | JWT (python-jose), Google OAuth 2.0 (Authlib)                     |
| **Email**    | FastAPI-Mail, Gmail SMTP with App Passwords                        |
| **Scheduler**| APScheduler                                                        |
| **UI Icons** | Lucide React                                                       |

---

## 📁 Project Structure

```
JobLense/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # Route handlers
│   │   │   ├── auth.py          # Login, register, OAuth flows
│   │   │   ├── resume.py        # Resume upload & retrieval
│   │   │   ├── ats.py           # ATS analysis endpoints
│   │   │   ├── jobs.py          # Job CRUD operations
│   │   │   └── recommendations.py  # AI job recommendations
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings (from .env)
│   │   │   ├── security.py      # JWT token creation & validation
│   │   │   ├── oauth.py         # Google/Facebook OAuth setup
│   │   │   ├── dependencies.py  # FastAPI dependency injection
│   │   │   └── scheduler.py     # APScheduler configuration
│   │   ├── db/
│   │   │   ├── models/          # SQLAlchemy ORM models
│   │   │   ├── mysql.py         # Async SQLAlchemy engine & session
│   │   │   └── mongodb.py       # Motor async MongoDB client
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic layer
│   │   │   ├── ats_service.py   # ATS scoring with Gemini AI
│   │   │   ├── auth_service.py  # User registration & login logic
│   │   │   ├── job_service.py   # Job application CRUD logic
│   │   │   ├── resume_service.py       # Resume file handling
│   │   │   ├── recommendation_service.py  # AI recommendations
│   │   │   ├── email_service.py # Email sending via SMTP
│   │   │   └── gemini_utils.py  # Gemini API client wrapper
│   │   └── tasks/
│   │       └── interview_reminder.py  # Scheduled reminder job
│   ├── alembic/                 # Database migrations
│   ├── uploads/                 # Uploaded resume files
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API client
│   │   ├── components/
│   │   │   ├── layout/          # Navbar, sidebar, page layout
│   │   │   ├── shared/          # Reusable components
│   │   │   └── ui/              # Buttons, spinners, inputs
│   │   ├── context/             # React context (AuthContext)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/
│   │   │   ├── Auth/            # Login, Register, OAuthCallback
│   │   │   ├── Dashboard/       # Main dashboard
│   │   │   ├── Resume/          # Upload & list resumes
│   │   │   ├── ATS/             # Quick check & detailed reports
│   │   │   ├── Jobs/            # Job list, create, edit, detail
│   │   │   └── Recommendations/ # AI-powered suggestions
│   │   ├── utils/               # Utility functions
│   │   ├── App.jsx              # Root routing component
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global styles & design tokens
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Google Cloud Console** project (for OAuth & Gemini API key)
- *(Optional)* MongoDB Atlas account for document storage

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/JobLense.git
cd JobLense
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
cp .env.example .env
```

Open `backend/.env` and fill in the required values:

| Variable               | Required | Description                                |
| ---------------------- | -------- | ------------------------------------------ |
| `SECRET_KEY`           | ✅       | Random 32+ character string for JWT signing |
| `GOOGLE_CLIENT_ID`     | ✅       | From Google Cloud Console                   |
| `GOOGLE_CLIENT_SECRET` | ✅       | From Google Cloud Console                   |
| `GOOGLE_REDIRECT_URI`  | ✅       | `http://localhost:8000/api/v1/auth/google/callback` |
| `GEMINI_API_KEY`       | ✅       | From [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `DATABASE_URL`         | ⬜       | Defaults to SQLite (`sqlite+aiosqlite:///./joblense.db`) |
| `MONGODB_URI`          | ⬜       | MongoDB connection string (optional)        |
| `MAIL_USERNAME`        | ⬜       | Gmail address for email notifications       |
| `MAIL_PASSWORD`        | ⬜       | Gmail App Password (16-char)                |

> 💡 See [`backend/OAUTH_SETUP.md`](backend/OAUTH_SETUP.md) for step-by-step Google OAuth & Gmail App Password setup instructions.

#### Start the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at **http://localhost:5173**.

---

## 🔗 API Endpoints

| Method   | Endpoint                             | Description                    |
| -------- | ------------------------------------ | ------------------------------ |
| `POST`   | `/api/v1/auth/register`             | Register a new user            |
| `POST`   | `/api/v1/auth/login`                | Login with email & password    |
| `POST`   | `/api/v1/auth/logout`               | Logout (clear cookie)          |
| `GET`    | `/api/v1/auth/me`                   | Get current user profile       |
| `GET`    | `/api/v1/auth/google/login`         | Initiate Google OAuth          |
| `GET`    | `/api/v1/auth/google/callback`      | Google OAuth callback          |
| `POST`   | `/api/v1/resume/upload`             | Upload a resume (PDF)          |
| `GET`    | `/api/v1/resume/list`               | List user's resumes            |
| `POST`   | `/api/v1/ats/quick-check`           | Run ATS analysis               |
| `GET`    | `/api/v1/ats/report/{id}`           | Get ATS report by ID           |
| `GET`    | `/api/v1/jobs`                      | List all job applications      |
| `POST`   | `/api/v1/jobs`                      | Create a job application       |
| `GET`    | `/api/v1/jobs/{id}`                 | Get job application details    |
| `PUT`    | `/api/v1/jobs/{id}`                 | Update a job application       |
| `DELETE` | `/api/v1/jobs/{id}`                 | Delete a job application       |
| `POST`   | `/api/v1/recommendations/generate`  | Generate AI recommendations    |
| `GET`    | `/api/v1/recommendations`           | Get recommendations            |
| `GET`    | `/health`                           | Health check                   |

> 📖 Full interactive API documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc) when the server is running.

---

## ⚙️ Configuration

### Database Options

**Development (SQLite — default, zero setup):**
```env
DATABASE_URL=sqlite+aiosqlite:///./joblense.db
```

**Production (MySQL):**
```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/joblense
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the **Google+ API** and **People API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set **Authorized redirect URI** to `http://localhost:8000/api/v1/auth/google/callback`
6. Copy the Client ID and Client Secret to your `.env` file

### Gemini AI Setup

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate an API key
3. Add it to your `.env` as `GEMINI_API_KEY`

---

## 🛠️ Development

### Running Both Servers

Open two terminals:

```bash
# Terminal 1 — Backend
cd backend
.venv\Scripts\activate     # or source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

### Database Migrations (Alembic)

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Build for Production

```bash
cd frontend
npm run build    # Output in dist/
```

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ using FastAPI + React + Gemini AI**

</div>
]]>
