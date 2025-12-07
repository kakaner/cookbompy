# CookBomPy

A personal book tracking application for a small group of readers, inspired by Goodreads and LibraryThing but designed for intimate use among friends.

## Features

- **Book Management**: Track books with ISBN lookup, custom summaries, ratings (1-10 with decimals), genres, and tags
- **Reading Status**: Mark books as to-read, reading, completed, or abandoned
- **Ownership Tracking**: Track whether books are owned physically, on Kindle, borrowed, or read elsewhere
- **Reviews**: Write HTML markdown reviews and recommendations
- **Reading Locations**: Record where you read each book
- **Comments & Threading**: Comment on each other's reads with nested reply threads
- **Analytics**: Public analytics showing reading stats, ownership percentages, ratings, genres, and user comparisons
- **Export**: Export all your data to TSV format
- **Authentication**: Username/email login and OAuth (Google, GitHub) support
- **Email Notifications**: Configurable email notifications for comments and mentions

## Tech Stack

- **Frontend**: Vue.js 3 with Vite, Vue Router, Pinia
- **Backend**: Python FastAPI
- **Database**: SQLite (local development), PostgreSQL (production/RDS compatible)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT tokens with OAuth support
- **Testing**: pytest (unit tests), Playwright (e2e tests)

## Project Structure

```
cookbompy/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Security, OAuth, email
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database setup
│   │   └── main.py       # FastAPI app
│   ├── migrations/       # Alembic migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/        # Vue pages
│   │   ├── stores/       # Pinia stores
│   │   ├── router/       # Vue Router
│   │   └── App.vue
│   └── package.json
├── tests/
│   ├── unit/             # Unit tests
│   └── e2e/              # E2E tests
└── README.md
```

## Setup Instructions

### Quick Start (Recommended)

Use the setup script for automated setup:
```bash
./setup.sh              # Normal setup
./setup.sh --reset-db   # Setup with database reset (deletes existing DB)
```

### Prerequisites

- Python 3.10+
- Node.js 18+
- SQLite 3 (included with Python, no separate installation needed)
- PostgreSQL (optional, for production/RDS deployment)

**Note**: On macOS, `pydantic-core` (a dependency of Pydantic v2) may require compilation. The setup script handles this gracefully. If installation fails, you can install Rust first: `brew install rust` or use pre-built wheels.

### Backend Setup

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   # Install base dependencies (includes Pydantic v2, SQLAlchemy 2.0)
   pip install -r requirements-base.txt
   
   # Optionally install PostgreSQL driver (only if using PostgreSQL)
   pip install psycopg2-binary
   ```
   
   Note: 
   - On macOS, `pydantic-core` may require compilation. If it fails, install Rust: `brew install rust`
   - If `psycopg2-binary` fails to install, you can skip it (SQLite works without it) or install PostgreSQL libraries: `brew install postgresql`
   - The setup script handles these issues automatically

3. **Configure environment** (optional):
   ```bash
   # The default uses SQLite (no configuration needed)
   # For PostgreSQL, create .env file:
   # cp .env.local .env
   # Edit .env and set DATABASE_URL to your PostgreSQL connection string
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```
   
   This will create a `cookbompy.db` file in the backend directory for SQLite.
   
   **To reset the database** (delete and recreate):
   ```bash
   # Option 1: Use the reset script
   ./reset_db.sh
   
   # Option 2: Manually delete and re-run migrations
   rm cookbompy.db  # Delete the database file
   alembic upgrade head  # Recreate it
   ```

5. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.local .env
   # Edit .env with your API URL
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Environment Configuration

### Backend Environments

- **Local** (`.env.local`): Development on local machine
- **Dev** (`.env.dev`): Development/staging environment
- **Prod** (`.env.prod`): Production environment

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `FRONTEND_URL`: Frontend application URL
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: OAuth credentials
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`: OAuth credentials
- `SMTP_*`: Email configuration

### Frontend Environments

- **Local** (`.env.local`): `VITE_API_BASE=http://localhost:8001/api`
- **Dev** (`.env.dev`): Development API URL
- **Prod** (`.env.prod`): Production API URL

## Running Tests

### Unit Tests

```bash
cd backend
pytest tests/unit/
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/oauth` - OAuth login
- `GET /api/auth/me` - Get current user

### Books
- `GET /api/books` - List books
- `GET /api/books/{id}` - Get book by ID
- `GET /api/books/isbn/{isbn}` - Get/lookup book by ISBN
- `GET /api/books/search` - Search books
- `POST /api/books` - Create book
- `PUT /api/books/{id}` - Update book

### User Books
- `GET /api/user-books/me` - Get current user's books
- `GET /api/user-books/user/{user_id}` - Get user's books (public)
- `GET /api/user-books/{id}` - Get user book entry
- `POST /api/user-books` - Add book to library
- `PUT /api/user-books/{id}` - Update user book entry
- `DELETE /api/user-books/{id}` - Remove book from library

### Comments
- `GET /api/comments/user-book/{user_book_id}` - Get comments
- `POST /api/comments` - Create comment
- `PUT /api/comments/{id}` - Update comment
- `DELETE /api/comments/{id}` - Delete comment

### Analytics
- `GET /api/analytics/user/{user_id}` - Get user analytics
- `GET /api/analytics/compare` - Compare users

### Export
- `GET /api/export/tsv` - Export user's books to TSV

### Users
- `GET /api/users` - List users
- `GET /api/users/{id}` - Get user profile
- `PUT /api/users/me` - Update current user

## Database Management

### Resetting the Database

To delete all data and recreate the database schema:

**Option 1: Use the reset script (Recommended)**
```bash
cd backend
./reset_db.sh
```

**Option 2: Use setup script with reset flag**
```bash
./setup.sh --reset-db
```

**Option 3: Manual reset**
```bash
cd backend
# Delete the database file (SQLite)
rm cookbompy.db

# Or for PostgreSQL, drop and recreate the database
# Then run migrations
alembic upgrade head
```

### Database Location

- **SQLite (default)**: `backend/cookbompy.db`
- **PostgreSQL**: Configured via `DATABASE_URL` in `.env`

### Troubleshooting Database Issues

If you encounter migration errors:

1. **Reset the database** (see above)
2. **Check for existing database file**: Make sure `cookbompy.db` is deleted before re-running migrations
3. **Verify virtual environment**: Ensure you're in the backend directory with venv activated
4. **Check Alembic version**: Ensure Alembic is installed: `pip install alembic`

## Database Schema

### Core Tables
- `users`: User accounts with OAuth support
- `books`: Book catalog
- `genres`: Book genres (imported and user-created)
- `tags`: User-created tags
- `user_books`: User's reading records
- `reading_locations`: Where books were read
- `user_book_comments`: Comments and nested threads

## Deployment

### Backend (FastAPI)

1. Set environment variables for production
2. Use a production ASGI server like Gunicorn with Uvicorn workers:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. Set up reverse proxy (nginx) for HTTPS

### Frontend (Vue)

1. Build for production:
   ```bash
   npm run build
   ```

2. Serve `dist/` directory with nginx or similar

### Database (RDS)

1. Create PostgreSQL RDS instance
2. Update `DATABASE_URL` in production environment
3. Run migrations:
   ```bash
   alembic upgrade head
   ```

## License

This project is for personal use.

## Contributing

This is a personal project for a small group. Contributions welcome from authorized users.

