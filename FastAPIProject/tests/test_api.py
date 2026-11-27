import pytest
import sqlite3
from fastapi.testclient import TestClient
from main import app, get_db

#Fixture to create a test database connection
@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_users.db"

    def test_get_db():
        conn = sqlite3.connect(str(db_file))
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    monkeypatch.setattr("main.get_db", test_get_db)

    # Создаём таблицы в тестовой базе
    conn = test_get_db()

    conn.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL
        );

        CREATE TABLE movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            release_year INTEGER,
            description TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER NOT NULL,
            comment TEXT,
            movie_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()

    with TestClient(app) as test_client:
        yield test_client


# FIXTURE: регистрация и авторизация тестового пользователя
@pytest.fixture
def auth_headers(client):
    client.post("/register", json={
        "username": "testuser",
        "password": "test123"
    })

    response = client.post("/login", data={
        "username": "testuser",
        "password": "test123"
    })

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# 1. Проверка главной страницы
def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "My first FastAPI project"


# 2. Успешная регистрация
def test_register(client):
    response = client.post("/register", json={
        "username": "danara",
        "password": "123456"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"


# 3. Повторная регистрация
def test_duplicate_register(client):
    data = {
        "username": "danara",
        "password": "123456"
    }

    client.post("/register", json=data)
    response = client.post("/register", json=data)

    assert response.status_code == 400


# 4. Параметризация проверки неверных данных
@pytest.mark.parametrize("data", [
    {"username": "test"},
    {"password": "123456"},
    {},
])
def test_invalid_register(client, data):
    response = client.post("/register", json=data)

    assert response.status_code == 422


# 5. Неверный пароль
def test_wrong_password(client):
    client.post("/register", json={
        "username": "testuser",
        "password": "correct123"
    })

    response = client.post("/login", data={
        "username": "testuser",
        "password": "wrong123"
    })

    assert response.status_code == 401


# 6. Получение профиля без авторизации
def test_profile_without_token(client):
    response = client.get("/profile")

    assert response.status_code == 401


# 7. Успешное получение профиля
def test_profile(client, auth_headers):
    response = client.get("/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


# 8. Получение пустого списка фильмов
def test_empty_movies(client):
    response = client.get("/movies")

    assert response.status_code == 200
    assert response.json() == []


# 9. Добавление фильма
def test_add_movie(client, auth_headers):
    response = client.post(
        "/movies",
        headers=auth_headers,
        json={
            "title": "Harry Potter",
            "genre": "Fantasy",
            "release_year": 2001,
            "description": "Magic story"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Harry Potter"


# 10. Несуществующий фильм
def test_update_missing_movie(client, auth_headers):
    response = client.put(
        "/movies/999",
        headers=auth_headers,
        json={
            "title": "Test",
            "genre": "Drama",
            "release_year": 2020,
            "description": "Test movie"
        }
    )

    assert response.status_code == 404


# 11. Получение пустого списка отзывов
def test_empty_reviews(client, auth_headers):
    response = client.get("/reviews", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


# 12. Отзыв к несуществующему фильму
def test_review_missing_movie(client, auth_headers):
    response = client.post(
        "/reviews",
        headers=auth_headers,
        json={
            "rating": 5,
            "comment": "Great movie",
            "movie_id": 999
        }
    )

    assert response.status_code == 404
