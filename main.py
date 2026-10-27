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
