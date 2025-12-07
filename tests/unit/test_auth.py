import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/auth/register", json=user_data)
    return response.json()


def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 201  # Phase 1: 201 Created
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "newuser@example.com"


def test_register_duplicate_username(client, test_user):
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "password123"
    })
    assert response.status_code == 400


# Note: Phase 1 uses simple bcrypt hashing without password length normalization
# These tests can be updated in later phases if needed


def test_login_success(client, test_user):
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()  # Phase 1: includes refresh token


def test_login_invalid_credentials(client, test_user):
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_with_email(client, test_user):
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()  # Phase 1: includes refresh token


def test_get_current_user(client, test_user):
    # Login first
    login_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert "id" in response.json()
    assert "email" in response.json()

