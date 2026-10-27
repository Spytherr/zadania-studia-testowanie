from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column("movieId", Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    genres: Mapped[str] = mapped_column(String(255), nullable=False)


class Link(Base):
    __tablename__ = "links"

    movie_id: Mapped[int] = mapped_column(
        "movieId", ForeignKey("movies.movieId"), primary_key=True
    )
    imdb_id: Mapped[str] = mapped_column("imdbId", String(7), nullable=False)
    tmdb_id: Mapped[int | None] = mapped_column("tmdbId", Integer)


class Rating(Base):
    __tablename__ = "ratings"

    user_id: Mapped[int] = mapped_column("userId", Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(
        "movieId", ForeignKey("movies.movieId"), primary_key=True
    )
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column("userId", Integer, nullable=False)
    movie_id: Mapped[int] = mapped_column(
        "movieId", ForeignKey("movies.movieId"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
