# Pastebin-Lite

A lightweight Pastebin-like application that allows users to create text pastes and share them through unique URLs. Pastes can optionally have an expiration time (TTL) and a maximum view limit.

**Live Application:** https://pastebin-lite-dun-pi.vercel.app

**GitHub Repository:** https://github.com/G-Aarush-Raj/pastebin-lite

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, Flask |
| Database | Neon PostgreSQL |
| ORM | Flask-SQLAlchemy |
| Deployment | Vercel |
| Version Control | Git, GitHub |

## Features

- Create text pastes and generate unique shareable URLs.
- Retrieve paste content through the API.
- View pastes through a dedicated HTML page.
- Optional time-based expiration (TTL).
- Optional maximum view-count restriction.
- Automatic paste unavailability when either constraint is reached.
- Input validation and JSON error responses.
- Safe HTML rendering to prevent script execution.
- Database-backed persistent storage.

## Running Locally

### Prerequisites

- Python 3.10 or later
- Node.js and npm
- A PostgreSQL database (Neon PostgreSQL can be used)

### 1. Clone the repository

```bash
git clone https://github.com/G-Aarush-Raj/pastebin-lite.git
cd pastebin-lite
```

### 2. Set up the backend

```bash
cd backend

python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory:

```env
DATABASE_URL=your_postgresql_connection_string
TEST_MODE=1
FRONTEND_ORIGIN=http://localhost:5173
```

Replace the database URL with your PostgreSQL connection string.

Start the Flask server:

```bash
python app.py
```

The backend runs at:

`http://127.0.0.1:5000`

### 3. Set up the frontend

Open a new terminal from the project root:

```bash
cd frontend
npm install
```

Create a `.env.local` file inside the `frontend` directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

Start the React development server:

```bash
npm run dev
```

The frontend runs at:

`http://localhost:5173`

## Persistence Layer

The application uses **Neon PostgreSQL** as its persistent database and Flask-SQLAlchemy as its ORM.

Paste records are stored in PostgreSQL rather than in application memory. This ensures that paste data remains available across application restarts and serverless function executions.

Database tables are initialized automatically by the Flask application.

## Important Design Decisions

1. **Persistent storage:** PostgreSQL is used to store paste content, expiration timestamps, maximum views, and view counts.
2. **Atomic view-count handling:** Database-level atomic updates are used when retrieving pastes through the API to enforce view limits safely under concurrent requests.
3. **Expiry handling:** Paste availability is checked using expiration timestamps and view-count constraints.
4. **Safe rendering:** HTML escaping is applied when displaying paste content to prevent script execution.
5. **Serverless deployment:** The frontend and backend are deployed as separate Vercel services within one project, with route-based rewrites directing requests to the appropriate service.
6. **Deterministic testing:** The `TEST_MODE` environment variable enables the `x-test-now-ms` request header for testing expiration behavior.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/healthz` | Database health check |
| POST | `/api/pastes` | Create a paste |
| GET | `/api/pastes/:id` | Retrieve a paste as JSON |
| GET | `/p/:id` | View a paste as HTML |

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `TEST_MODE` | Enables deterministic expiry testing when set to `1` |
| `FRONTEND_ORIGIN` | Allowed frontend origin for local CORS configuration |
| `VITE_API_BASE_URL` | Backend URL used by the frontend during local development |

**Note:** Environment files containing credentials are excluded from version control. Never commit database connection strings or secrets.

## Deployment

The application is deployed on Vercel using a multi-service configuration defined in `vercel.json`.

- Frontend: React + Vite
- Backend: Python Flask
- Database: Neon PostgreSQL

**Live URL:** https://pastebinlite-liard.vercel.app

---

Developed as part of a full-stack software engineering take-home assignment.
