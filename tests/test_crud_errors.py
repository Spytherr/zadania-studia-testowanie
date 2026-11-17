import pytest
from sqlalchemy import delete, select

from models import Link, Movie, Rating, Tag


def database_snapshot(session_factory):
    with session_factory() as session:
        return {
            model.__tablename__: session.execute(
                select(model.__table__).order_by(*model.__table__.primary_key.columns)
            ).all()
            for model in (Movie, Link, Rating, Tag)
        }


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
@pytest.mark.parametrize(
    "path,payload,detail",
    [
        (
            "/movies/999", {"id": 999, "title": "Missing", "genres": "Drama"},
            "Movie not found",
        ),
        (
            "/links/999", {"movieId": 999, "imdbId": "1234567", "tmdbId": 1},
            "Link not found",
        ),
        (
            "/ratings/999/1",
            {"user_id": 999, "movie_id": 1, "rating": 4.0, "timestamp": 1000},
            "Rating not found",
        ),
        (
            "/ratings/1/999",
            {"user_id": 1, "movie_id": 999, "rating": 4.0, "timestamp": 1000},
            "Rating not found",
        ),
        (
            "/tags/999",
            {"userId": 1, "movieId": 1, "tag": "missing", "timestamp": 1000},
            "Tag not found",
        ),
    ],
    ids=["movie", "link", "rating-user", "rating-movie", "tag"],
)
def test_missing_resource_returns_404(client, session_factory, method, path, payload, detail):
    before = database_snapshot(session_factory)
    kwargs = {"json": payload} if method == "PUT" else {}

    response = client.request(method, path, **kwargs)

    assert response.status_code == 404
    assert response.json() == {"detail": detail}
    assert database_snapshot(session_factory) == before


@pytest.mark.parametrize(
    "path,payload,detail",
    [
        (
            "/movies", {"id": 1, "title": "Duplicate", "genres": "Drama"},
            "Movie with this id already exists",
        ),
        (
            "/links", {"movieId": 1, "imdbId": "1234567", "tmdbId": 1},
            "Link with this movieId already exists",
        ),
        (
            "/ratings",
            {"user_id": 1, "movie_id": 1, "rating": 1.0, "timestamp": 4000},
            "This user has already rated this movie",
        ),
    ],
    ids=["movie", "link", "rating"],
)
def test_create_duplicate_returns_409(client, session_factory, path, payload, detail):
    before = database_snapshot(session_factory)

    response = client.post(path, json=payload)

    assert response.status_code == 409
    assert response.json() == {"detail": detail}
    assert database_snapshot(session_factory) == before


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("POST", "/links", {"movieId": 999, "imdbId": "1234567", "tmdbId": 1}),
        (
            "POST", "/ratings",
            {"user_id": 3, "movie_id": 999, "rating": 4.0, "timestamp": 1000},
        ),
        (
            "POST", "/tags",
            {"userId": 1, "movieId": 999, "tag": "missing", "timestamp": 1000},
        ),
        (
            "PUT", "/tags/1",
            {"userId": 1, "movieId": 999, "tag": "missing", "timestamp": 1000},
        ),
    ],
    ids=["create-link", "create-rating", "create-tag", "update-tag"],
)
def test_write_for_missing_movie_returns_404(client, session_factory, method, path, payload):
    before = database_snapshot(session_factory)

    response = client.request(method, path, json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}
    assert database_snapshot(session_factory) == before


@pytest.mark.parametrize(
    "path,payload,detail",
    [
        (
            "/links/1", {"movieId": 2, "imdbId": "1234567", "tmdbId": 1},
            "The URL movie_id must match the body movieId",
        ),
        (
            "/ratings/1/1",
            {"user_id": 2, "movie_id": 1, "rating": 4.0, "timestamp": 1000},
            "The URL identifiers must match the body identifiers",
        ),
        (
            "/ratings/1/1",
            {"user_id": 1, "movie_id": 2, "rating": 4.0, "timestamp": 1000},
            "The URL identifiers must match the body identifiers",
        ),
    ],
    ids=["link-movie", "rating-user", "rating-movie"],
)
def test_update_with_mismatched_ids_returns_400(client, session_factory, path, payload, detail):
    before = database_snapshot(session_factory)

    response = client.put(path, json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": detail}
    assert database_snapshot(session_factory) == before


@pytest.mark.parametrize("method", ["POST", "PUT"])
@pytest.mark.parametrize(
    "collection,item,payload,field",
    [
        ("/movies", "/movies/1", {"id": 1, "title": "", "genres": "Drama"}, "title"),
        (
            "/links", "/links/1",
            {"movieId": 1, "imdbId": "12345678", "tmdbId": 1}, "imdbId",
        ),
        (
            "/ratings", "/ratings/1/1",
            {"user_id": 1, "movie_id": 1, "rating": 5.5, "timestamp": 1000}, "rating",
        ),
        (
            "/tags", "/tags/1",
            {"userId": 1, "movieId": 1, "tag": "", "timestamp": 1000}, "tag",
        ),
    ],
    ids=["movie", "link", "rating", "tag"],
)
def test_invalid_body_returns_422(
    client, session_factory, method, collection, item, payload, field,
):
    before = database_snapshot(session_factory)

    response = client.request(method, collection if method == "POST" else item, json=payload)

    assert response.status_code == 422
    assert any(error["loc"] == ["body", field] for error in response.json()["detail"])
    assert database_snapshot(session_factory) == before


@pytest.mark.parametrize("path", ["/movies", "/links", "/ratings", "/tags"])
def test_get_empty_collection_returns_empty_list(client, db_session, path):
    for model in (Tag, Rating, Link, Movie):
        db_session.execute(delete(model))
    db_session.commit()

    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == []
    assert len(response.json()) == 0
