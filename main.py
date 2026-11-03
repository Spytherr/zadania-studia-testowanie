from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine, get_db
from load_data import load_data
from models import Link, Movie, Rating, Tag
from schemas import (
    LinkCreate,
    LinkResponse,
    MovieCreate,
    MovieResponse,
    RatingCreate,
    RatingResponse,
    TagCreate,
    TagResponse,
)


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


@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    return {
        "id": movie.id,
        "title": movie.title,
        "genre": movie.genres,
    }


@app.post("/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(movie_data: MovieCreate, db: Session = Depends(get_db)):
    if db.get(Movie, movie_data.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie with this id already exists",
        )

    movie = Movie(
        id=movie_data.id,
        title=movie_data.title,
        genres=movie_data.genres,
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)

    return {
        "id": movie.id,
        "title": movie.title,
        "genre": movie.genres,
    }
@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, movie_data: MovieCreate, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    movie.title = movie_data.title
    movie.genres = movie_data.genres
    db.commit()
    db.refresh(movie)

    return {
        "id": movie.id,
        "title": movie.title,
        "genre": movie.genres,
    }
@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    db.delete(movie)
    db.commit()

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

@app.get("/links/{movie_id}", response_model=LinkResponse)
def get_link(movie_id: int, db: Session = Depends(get_db)):
    link = db.get(Link, movie_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    return {
        "movieId": link.movie_id,
        "imdbId": link.imdb_id,
        "tmdbId": link.tmdb_id,
    }


@app.put("/links/{movie_id}", response_model=LinkResponse)
def update_link(
    movie_id: int,
    link_data: LinkCreate,
    db: Session = Depends(get_db),
):
    if movie_id != link_data.movieId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The URL movie_id must match the body movieId",
        )

    link = db.get(Link, movie_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    link.imdb_id = link_data.imdbId
    link.tmdb_id = link_data.tmdbId
    db.commit()
    db.refresh(link)

    return {
        "movieId": link.movie_id,
        "imdbId": link.imdb_id,
        "tmdbId": link.tmdb_id,
    }


@app.post("/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_link(link_data: LinkCreate, db: Session = Depends(get_db)):
    if db.get(Movie, link_data.movieId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    if db.get(Link, link_data.movieId) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Link with this movieId already exists",
        )

    link = Link(
        movie_id=link_data.movieId,
        imdb_id=link_data.imdbId,
        tmdb_id=link_data.tmdbId,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    return {
        "movieId": link.movie_id,
        "imdbId": link.imdb_id,
        "tmdbId": link.tmdb_id,
    }

@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(movie_id: int, db: Session = Depends(get_db)):
    link = db.get(Link, movie_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    db.delete(link)
    db.commit()

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


@app.get(
    "/ratings/{user_id}/{movie_id}",
    response_model=RatingResponse,
)
def get_rating(user_id: int, movie_id: int, db: Session = Depends(get_db)):
    rating = db.get(Rating, (user_id, movie_id))
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
        )

    return {
        "userId": rating.user_id,
        "movieId": rating.movie_id,
        "rating": rating.rating,
        "timestamp": rating.timestamp,
    }


@app.post(
    "/ratings",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rating(rating_data: RatingCreate, db: Session = Depends(get_db)):
    if db.get(Movie, rating_data.movie_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    if db.get(Rating, (rating_data.user_id, rating_data.movie_id)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user has already rated this movie",
        )

    rating = Rating(
        user_id=rating_data.user_id,
        movie_id=rating_data.movie_id,
        rating=rating_data.rating,
        timestamp=rating_data.timestamp,
    )
    db.add(rating)
    db.commit()

    return {
        "userId": rating.user_id,
        "movieId": rating.movie_id,
        "rating": rating.rating,
        "timestamp": rating.timestamp,
    }


@app.put(
    "/ratings/{user_id}/{movie_id}",
    response_model=RatingResponse,
)
def update_rating(
    user_id: int,
    movie_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
):
    if (user_id, movie_id) != (rating_data.user_id, rating_data.movie_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The URL identifiers must match the body identifiers",
        )

    rating = db.get(Rating, (user_id, movie_id))
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
        )

    rating.rating = rating_data.rating
    rating.timestamp = rating_data.timestamp
    db.commit()
    db.refresh(rating)

    return {
        "userId": rating.user_id,
        "movieId": rating.movie_id,
        "rating": rating.rating,
        "timestamp": rating.timestamp,
    }


@app.delete(
    "/ratings/{user_id}/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rating(user_id: int, movie_id: int, db: Session = Depends(get_db)):
    rating = db.get(Rating, (user_id, movie_id))
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
        )

    db.delete(rating)
    db.commit()


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


@app.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return {
        "id": tag.id,
        "userId": tag.user_id,
        "movieId": tag.movie_id,
        "tag": tag.tag,
        "timestamp": tag.timestamp,
    }


@app.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    if db.get(Movie, tag_data.movieId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    tag = Tag(
        user_id=tag_data.userId,
        movie_id=tag_data.movieId,
        tag=tag_data.tag,
        timestamp=tag_data.timestamp,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {
        "id": tag.id,
        "userId": tag.user_id,
        "movieId": tag.movie_id,
        "tag": tag.tag,
        "timestamp": tag.timestamp,
    }


@app.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_data: TagCreate,
    db: Session = Depends(get_db),
):
    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    if db.get(Movie, tag_data.movieId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    tag.user_id = tag_data.userId
    tag.movie_id = tag_data.movieId
    tag.tag = tag_data.tag
    tag.timestamp = tag_data.timestamp
    db.commit()
    db.refresh(tag)

    return {
        "id": tag.id,
        "userId": tag.user_id,
        "movieId": tag.movie_id,
        "tag": tag.tag,
        "timestamp": tag.timestamp,
    }


@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    db.delete(tag)
    db.commit()
