from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine, get_db
from load_data import load_data
from models import Link, Movie, Rating, Tag


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data()
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/hello")
def hello():
    return {"hello": "world"}


@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    return [
        {"id": movie.id, "title": movie.title, "genre": movie.genres}
        for movie in db.scalars(select(Movie).order_by(Movie.id))
    ]

@app.get("/links")
def get_links(db: Session = Depends(get_db)):
    return [
        {
            "movieId": link.movie_id,
            "imdbId": link.imdb_id,
            "tmdbId": link.tmdb_id,
        }
        for link in db.scalars(select(Link).order_by(Link.movie_id))
    ]

@app.get("/ratings")
def get_ratings(db: Session = Depends(get_db)):
    return [
        {
            "userId": rating.user_id,
            "movieId": rating.movie_id,
            "rating": rating.rating,
            "timestamp": rating.timestamp,
        }
        for rating in db.scalars(
            select(Rating).order_by(Rating.user_id, Rating.movie_id)
        )
    ]

@app.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    return [
        {
            "userId": tag.user_id,
            "movieId": tag.movie_id,
            "tag": tag.tag,
            "timestamp": tag.timestamp,
        }
        for tag in db.scalars(select(Tag).order_by(Tag.id))
    ]
