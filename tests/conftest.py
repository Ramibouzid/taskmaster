import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models import User


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def auth_headers(client):
    return {"X-CSRFToken": "test-csrf"}


@pytest.fixture
def registered_user(app):
    with app.app_context():
        user = User(name="Test", email="test@test.com")
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        return user


@pytest.fixture
def logged_in_client(client, registered_user):
    with client:
        client.post("/login", data={
            "email": "test@test.com",
            "password": "password123",
        })
    return client
