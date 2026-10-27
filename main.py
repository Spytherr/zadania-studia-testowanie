import csv

from pathlib import Path

from fastapi import FastAPI

from movieDTO import Movie

app = FastAPI()


@app.get("/hello")
def hello():
    return {"hello": "world"}


@app.get("/movies")
def get_movies():
    movies_file = Path(__file__).with_name("movies.csv")
    with movies_file.open(encoding="utf-8") as file:
        movies_data = csv.DictReader(file)
        data = list(movies_data)
        

    movies = []
    for movie_data in data:
        movie = Movie(
            movie_id=movie_data["movieId"],
            title=movie_data["title"],
            genre=movie_data["genres"],
        )
        movies.append(movie.__dict__)

    return movies

@app.get("/links")
def get_links():
    links_file = Path(__file__).with_name("links.csv")
    with links_file.open(encoding="utf-8") as file:
        links_data = csv.DictReader(file)
        data = list(links_data)

    return data

@app.get("/ratings")
def get_ratings():
    ratings_file = Path(__file__).with_name("ratings.csv")
    with ratings_file.open(encoding="utf-8") as file:
        ratings_data = csv.DictReader(file)
        data = list(ratings_data)

    return data

@app.get("/tags")
def get_tags():
    tags_file = Path(__file__).with_name("tags.csv")
    with tags_file.open(encoding="utf-8") as file:
        tags_data = csv.DictReader(file)
        data = list(tags_data)

    return data