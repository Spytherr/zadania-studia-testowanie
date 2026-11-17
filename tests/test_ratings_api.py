from sqlalchemy import func, select

from models import Rating


def test_get_ratings_returns_fixture_records(client, ratings):
    response = client.get("/ratings")

    assert response.status_code == 200
    assert len(response.json()) == len(ratings)
    assert response.json() == ratings


def test_get_rating_returns_existing_composite_id(client, ratings):
    rating = ratings[0]
    response = client.get(f"/ratings/{rating['userId']}/{rating['movieId']}")

    assert response.status_code == 200
    assert (response.json()["userId"], response.json()["movieId"]) == (1, 1)
    assert response.json() == rating


def test_create_rating_persists_record(client, db_session, ratings):
    payload = {"user_id": 3, "movie_id": 3, "rating": 4.0, "timestamp": 4000}
    response = client.post("/ratings", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "userId": 3, "movieId": 3, "rating": 4.0, "timestamp": 4000,
    }
    saved = db_session.get(Rating, (3, 3))
    assert saved is not None
    assert (saved.rating, saved.timestamp) == (payload["rating"], payload["timestamp"])
    assert db_session.scalar(select(func.count()).select_from(Rating)) == len(ratings) + 1


def test_update_rating_persists_changes(client, db_session, ratings):
    payload = {"user_id": 1, "movie_id": 1, "rating": 2.5, "timestamp": 5000}
    response = client.put("/ratings/1/1", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "userId": 1, "movieId": 1, "rating": 2.5, "timestamp": 5000,
    }
    saved = db_session.get(Rating, (1, 1))
    assert saved is not None
    assert (saved.rating, saved.timestamp) == (payload["rating"], payload["timestamp"])
    assert db_session.scalar(select(func.count()).select_from(Rating)) == len(ratings)
    # The other half of the composite key must not select a different rating.
    assert db_session.get(Rating, (1, 2)).rating == ratings[1]["rating"]
    assert db_session.get(Rating, (2, 1)).rating == ratings[2]["rating"]


def test_delete_rating_removes_record(client, db_session, ratings):
    response = client.delete("/ratings/1/1")

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.get(Rating, (1, 1)) is None
    assert db_session.get(Rating, (1, 2)) is not None
    assert db_session.get(Rating, (2, 1)) is not None
    assert db_session.scalar(select(func.count()).select_from(Rating)) == len(ratings) - 1
    missing = client.get("/ratings/1/1")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Rating not found"}
