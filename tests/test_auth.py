def test_register_page(client):
    rv = client.get("/register")
    assert rv.status_code == 200


def test_register(client):
    rv = client.post("/register", data={
        "name": "New User",
        "email": "new@test.com",
        "password": "password123",
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Account created" in rv.data


def test_register_duplicate(client, registered_user):
    rv = client.post("/register", data={
        "name": "Test",
        "email": "test@test.com",
        "password": "password123",
    }, follow_redirects=True)
    assert b"already registered" in rv.data


def test_login_page(client):
    rv = client.get("/login")
    assert rv.status_code == 200


def test_login(client, registered_user):
    rv = client.post("/login", data={
        "email": "test@test.com",
        "password": "password123",
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Dashboard" in rv.data or b"logged in" in rv.data


def test_login_invalid(client):
    rv = client.post("/login", data={
        "email": "wrong@test.com",
        "password": "wrong",
    }, follow_redirects=True)
    assert b"Invalid email" in rv.data


def test_logout(client, registered_user):
    client.post("/login", data={
        "email": "test@test.com",
        "password": "password123",
    })
    rv = client.get("/logout", follow_redirects=True)
    assert rv.status_code == 200


def test_dashboard_requires_login(client):
    rv = client.get("/dashboard", follow_redirects=True)
    assert b"Login" in rv.data or b"log in" in rv.data.lower()


def test_register_creates_tables_automatically():
    from app import create_app
    from app.config import TestConfig
    app = create_app(TestConfig)
    with app.test_client() as client:
        rv = client.post("/register", data={
            "name": "Auto Tables",
            "email": "auto@test.com",
            "password": "password123",
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert b"Account created" in rv.data
