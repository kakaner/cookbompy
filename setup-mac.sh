#!/bin/bash

# CookBomPy Setup Script for macOS
# This script sets up the development environment for Phase 0-1

set -e  # Exit on error

echo "🚀 CookBomPy Setup for macOS"
echo "============================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠ Warning: This script is designed for macOS${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required tools
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "   Install with: brew install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Found $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "   Install with: brew install node"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Found Node.js $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓${NC} Found npm $NPM_VERSION"

echo ""
echo "🔧 Setting up backend..."
echo "------------------------"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "vv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv vv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source vv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
echo "Installing Python dependencies..."
if pip install -r requirements.txt --quiet; then
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Some dependencies may have failed. Continuing..."
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# CookBomPy Environment Variables
DATABASE_URL=sqlite:///./cookbompy.db
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
APP_NAME=CookBomPy
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
ENVIRONMENT=local
DEBUG=True
EOF
    echo -e "${GREEN}✓${NC} .env file created with secure SECRET_KEY"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Run database migrations
echo "Running database migrations..."
if alembic upgrade head; then
    echo -e "${GREEN}✓${NC} Database migrations completed"
else
    echo -e "${YELLOW}⚠${NC} Migration may have failed. Check the output above."
fi

cd ..

echo ""
echo "🎨 Setting up frontend..."
echo "------------------------"

cd frontend

# Install npm dependencies
echo "Installing npm dependencies..."
if npm install --silent; then
    echo -e "${GREEN}✓${NC} npm dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} npm install had issues. Check the output above."
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "=============="
echo ""
echo "1. Start the backend server:"
echo "   cd backend"
echo "   source vv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:5173"
echo ""
echo "📚 Useful commands:"
echo "   - Reset database: cd backend && alembic downgrade base && alembic upgrade head"
echo "   - View API docs: http://localhost:8000/docs"
echo "   - Health check: http://localhost:8000/api/health"
echo ""
echo "🎉 Happy coding!"

