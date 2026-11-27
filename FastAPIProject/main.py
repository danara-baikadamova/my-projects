
import requests
import sqlite3
import bcrypt

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel


app = FastAPI()

SECRET_KEY = "my_secret_key_12345"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# DATABASE

def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            release_year INTEGER,
            description TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER NOT NULL,
            comment TEXT,
            movie_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# MODELS

class User(BaseModel):
    username: str
    password: str


class Movie(BaseModel):
    title: str
    genre: str = "Unknown"
    release_year: int
    description: str


class Review(BaseModel):
    rating: int
    comment: str
    movie_id: int


# REGISTER

@app.post("/register")
def register(user: User):
    conn = get_db()
    cursor = conn.cursor()

    password_bytes = user.password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (user.username, hashed)
        )
        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    conn.close()

    return {"message": "User registered successfully"}


# LOGIN

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (form_data.username,)
    )

    result = cursor.fetchone()
    conn.close()

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Username does not exist"
        )

    password_bytes = form_data.password.encode("utf-8")
    stored_hash = result[0]

    if bcrypt.checkpw(password_bytes, stored_hash):
        token = jwt.encode(
            {
                "sub": form_data.username,
                "exp": datetime.utcnow() + timedelta(minutes=30)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    raise HTTPException(
        status_code=401,
        detail="Incorrect password"
    )


# AUTHENTICATION

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# USER PROFILE

@app.get("/profile")
def get_profile(username: str = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return {
        "id": user[0],
        "username": user[1],
        "message": "protected data"
    }


# HOME

@app.get("/")
def home():
    return {"message": "My first FastAPI project"}


# GET MOVIES

@app.get("/movies")
def get_movies():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    conn.close()

    return movies


# POST MOVIE

@app.post("/movies")
def add_movie(
    movie: Movie,
    username: str = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.execute(
        """
        INSERT INTO movies
        (title, genre, release_year, description, user_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            movie.title,
            movie.genre,
            movie.release_year,
            movie.description,
            user[0]
        )
    )

    conn.commit()
    movie_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Movie added successfully",
        "movie_id": movie_id,
        "title": movie.title,
        "genre": movie.genre
    }


# PUT MOVIE

@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    movie: Movie,
    username: str = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.execute(
        "SELECT id FROM movies WHERE id = ? AND user_id = ?",
        (movie_id, user[0])
    )

    existing_movie = cursor.fetchone()

    if existing_movie is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    cursor.execute(
        """
        UPDATE movies
        SET title = ?, genre = ?, release_year = ?, description = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            movie.title,
            movie.genre,
            movie.release_year,
            movie.description,
            movie_id,
            user[0]
        )
    )

    conn.commit()
    conn.close()

    return {"message": "Movie updated successfully"}


# DELETE MOVIE

@app.delete("/movies/{movie_id}")
def delete_movie(
    movie_id: int,
    username: str = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.execute(
        "DELETE FROM movies WHERE id = ? AND user_id = ?",
        (movie_id, user[0])
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    conn.commit()
    conn.close()

    return {"message": "Movie deleted successfully"}


# GET REVIEWS

@app.get("/reviews")
def get_reviews(username: str = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reviews
        WHERE user_id = (
            SELECT id FROM users WHERE username = ?
        )
    """, (username,))

    reviews = cursor.fetchall()
    conn.close()

    return reviews


# POST REVIEWS

@app.post("/reviews")
def add_review(
    review: Review,
    username: str = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.execute(
        "SELECT id FROM movies WHERE id = ?",
        (review.movie_id,)
    )

    movie = cursor.fetchone()

    if movie is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    cursor.execute(
        """
        INSERT INTO reviews (rating, comment, movie_id, user_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            review.rating,
            review.comment,
            review.movie_id,
            user[0]
        )
    )

    conn.commit()
    review_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Review added successfully",
        "review_id": review_id
    }


# POKEMON API

@app.get("/pokemon/{name}")
def get_pokemon(name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            return {
                "id": data["id"],
                "name": data["name"],
                "height": data["height"],
                "weight": data["weight"]
            }

        raise HTTPException(
            status_code=404,
            detail="Pokemon not found"
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Pokemon API is unavailable"
        )
