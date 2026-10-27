import csv
from pathlib import Path

from sqlalchemy import select

from database import SessionLocal, create_tables
from models import Link, Movie, Rating, Tag


DATA_DIR = Path(__file__).resolve().parent


def _read_csv(filename: str) -> list[dict[str, str]]:
    with (DATA_DIR / filename).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def load_data() -> None:
    create_tables()
    with SessionLocal.begin() as session:
        if session.scalar(select(Movie.id).limit(1)) is not None:
            return

        session.add_all(
            Movie(
                id=int(row["movieId"]),
                title=row["title"],
                genres=row["genres"],
            )
            for row in _read_csv("movies.csv")
        )
        session.add_all(
            Link(
                movie_id=int(row["movieId"]),
                imdb_id=row["imdbId"],
                tmdb_id=int(row["tmdbId"]) if row["tmdbId"] else None,
            )
            for row in _read_csv("links.csv")
        )
        session.add_all(
            Rating(
                user_id=int(row["userId"]),
                movie_id=int(row["movieId"]),
                rating=float(row["rating"]),
                timestamp=int(row["timestamp"]),
            )
            for row in _read_csv("ratings.csv")
        )
        session.add_all(
            Tag(
                user_id=int(row["userId"]),
                movie_id=int(row["movieId"]),
                tag=row["tag"],
                timestamp=int(row["timestamp"]),
            )
            for row in _read_csv("tags.csv")
        )


if __name__ == "__main__":
    load_data()
    print("Baza SQLite została utworzona i załadowana danymi.")
