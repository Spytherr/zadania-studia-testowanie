import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main
from database import Base, get_db
from models import Link, Movie, Rating, Tag


@pytest.fixture
def movies():
    return [
        {"id": 1, "title": "Toy Story", "genres": "Animation|Comedy"},
        {"id": 2, "title": "Jumanji", "genres": "Adventure|Fantasy"},
        {"id": 3, "title": "Heat", "genres": "Action|Crime"},
    ]


@pytest.fixture
def links():
    return [
        {"movieId": 1, "imdbId": "0114709", "tmdbId": 862},
        {"movieId": 2, "imdbId": "0113497", "tmdbId": None},
    ]


@pytest.fixture
def ratings():
    return [
        {"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": 1000},
        {"userId": 1, "movieId": 2, "rating": 3.0, "timestamp": 2000},
        {"userId": 2, "movieId": 1, "rating": 5.0, "timestamp": 3000},
    ]


@pytest.fixture
def tags():
    return [
        {"id": 1, "userId": 1, "movieId": 1, "tag": "funny", "timestamp": 1000},
        {"id": 2, "userId": 2, "movieId": 2, "tag": "adventure", "timestamp": 2000},
    ]


@pytest.fixture
def test_engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def session_factory(test_engine):
    return sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def seeded_db(session_factory, movies, links, ratings, tags):
    with session_factory.begin() as session:
        session.add_all(Movie(**movie) for movie in movies)
        session.flush()
        session.add_all(
            Link(movie_id=row["movieId"], imdb_id=row["imdbId"], tmdb_id=row["tmdbId"])
            for row in links
        )
        session.add_all(
            Rating(
                user_id=row["userId"], movie_id=row["movieId"],
                rating=row["rating"], timestamp=row["timestamp"],
            )
            for row in ratings
        )
        session.add_all(
            Tag(
                id=row["id"], user_id=row["userId"], movie_id=row["movieId"],
                tag=row["tag"], timestamp=row["timestamp"],
            )
            for row in tags
        )


@pytest.fixture
def db_session(session_factory, seeded_db):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory, seeded_db, test_engine, monkeypatch):
    def override_get_db():
        with session_factory() as session:
            yield session

    monkeypatch.setattr(main, "load_data", lambda: None)
    monkeypatch.setattr(main, "engine", test_engine)
    previous_overrides = main.app.dependency_overrides.copy()
    main.app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.clear()
        main.app.dependency_overrides.update(previous_overrides)
