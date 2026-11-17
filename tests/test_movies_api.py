from sqlalchemy import func, select

from models import Movie


def test_get_movies_returns_fixture_records(client, movies):
    response = client.get("/movies")

    assert response.status_code == 200
    assert len(response.json()) == len(movies)
    assert response.json() == [
        {"id": row["id"], "title": row["title"], "genre": row["genres"]}
        for row in movies
    ]


def test_get_movie_returns_existing_id(client, movies):
    movie = movies[0]
    response = client.get(f"/movies/{movie['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == movie["id"]
    assert response.json() == {
        "id": movie["id"], "title": movie["title"], "genre": movie["genres"],
    }


def test_create_movie_persists_record(client, db_session, movies):
    payload = {"id": 4, "title": "Arrival", "genres": "Drama|Sci-Fi"}
    response = client.post("/movies", json=payload)

    assert response.status_code == 201
    assert response.json() == {"id": 4, "title": "Arrival", "genre": "Drama|Sci-Fi"}
    saved = db_session.get(Movie, 4)
    assert saved is not None
    assert (saved.title, saved.genres) == (payload["title"], payload["genres"])
    assert db_session.scalar(select(func.count()).select_from(Movie)) == len(movies) + 1


def test_update_movie_persists_changes(client, db_session, movies):
    payload = {"id": 1, "title": "Toy Story updated", "genres": "Animation"}
    response = client.put("/movies/1", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": payload["title"], "genre": "Animation"}
    saved = db_session.get(Movie, 1)
    assert saved is not None
    assert (saved.title, saved.genres) == (payload["title"], payload["genres"])
    assert db_session.scalar(select(func.count()).select_from(Movie)) == len(movies)


def test_delete_movie_removes_record(client, db_session, movies):
    response = client.delete("/movies/3")

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.get(Movie, 3) is None
    assert db_session.scalar(select(func.count()).select_from(Movie)) == len(movies) - 1
    missing = client.get("/movies/3")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Movie not found"}
