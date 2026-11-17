from sqlalchemy import func, select

from models import Link


def test_get_links_returns_fixture_records(client, links):
    response = client.get("/links")

    assert response.status_code == 200
    assert len(response.json()) == len(links)
    assert response.json() == links


def test_get_link_returns_existing_id(client, links):
    link = links[0]
    response = client.get(f"/links/{link['movieId']}")

    assert response.status_code == 200
    assert response.json()["movieId"] == link["movieId"]
    assert response.json() == link


def test_create_link_persists_record(client, db_session, links):
    payload = {"movieId": 3, "imdbId": "0113277", "tmdbId": 949}
    response = client.post("/links", json=payload)

    assert response.status_code == 201
    assert response.json() == payload
    saved = db_session.get(Link, 3)
    assert saved is not None
    assert (saved.imdb_id, saved.tmdb_id) == (payload["imdbId"], payload["tmdbId"])
    assert db_session.scalar(select(func.count()).select_from(Link)) == len(links) + 1


def test_update_link_persists_changes(client, db_session, links):
    payload = {"movieId": 1, "imdbId": "1234567", "tmdbId": None}
    response = client.put("/links/1", json=payload)

    assert response.status_code == 200
    assert response.json() == payload
    saved = db_session.get(Link, 1)
    assert saved is not None
    assert saved.imdb_id == payload["imdbId"]
    assert saved.tmdb_id is None
    assert db_session.scalar(select(func.count()).select_from(Link)) == len(links)


def test_delete_link_removes_record(client, db_session, links):
    response = client.delete("/links/1")

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.get(Link, 1) is None
    assert db_session.scalar(select(func.count()).select_from(Link)) == len(links) - 1
    missing = client.get("/links/1")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Link not found"}
