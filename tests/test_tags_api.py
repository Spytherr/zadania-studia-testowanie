from sqlalchemy import func, select

from models import Tag


def test_get_tags_returns_fixture_records(client, tags):
    response = client.get("/tags")

    assert response.status_code == 200
    assert len(response.json()) == len(tags)
    assert response.json() == [
        {key: value for key, value in row.items() if key != "id"}
        for row in tags
    ]


def test_get_tag_returns_existing_id(client, tags):
    tag = tags[0]
    response = client.get(f"/tags/{tag['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == tag["id"]
    assert response.json() == tag


def test_create_tag_persists_record(client, db_session, tags):
    payload = {"userId": 3, "movieId": 3, "tag": "thriller", "timestamp": 4000}
    response = client.post("/tags", json=payload)

    assert response.status_code == 201
    tag_id = response.json()["id"]
    assert isinstance(tag_id, int)
    assert tag_id not in {tag["id"] for tag in tags}
    assert response.json() == {"id": tag_id, **payload}
    saved = db_session.get(Tag, tag_id)
    assert saved is not None
    assert (saved.user_id, saved.movie_id, saved.tag, saved.timestamp) == (3, 3, "thriller", 4000)
    assert db_session.scalar(select(func.count()).select_from(Tag)) == len(tags) + 1


def test_update_tag_persists_changes(client, db_session, tags):
    payload = {"userId": 3, "movieId": 3, "tag": "updated", "timestamp": 5000}
    response = client.put("/tags/1", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": 1, **payload}
    saved = db_session.get(Tag, 1)
    assert saved is not None
    assert (saved.user_id, saved.movie_id, saved.tag, saved.timestamp) == (3, 3, "updated", 5000)
    assert db_session.scalar(select(func.count()).select_from(Tag)) == len(tags)


def test_delete_tag_removes_record(client, db_session, tags):
    response = client.delete("/tags/1")

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.get(Tag, 1) is None
    assert db_session.scalar(select(func.count()).select_from(Tag)) == len(tags) - 1
    missing = client.get("/tags/1")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Tag not found"}
