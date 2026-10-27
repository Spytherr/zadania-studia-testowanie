class linkDTO:
    def __init__(self, movieId,imdbId,tmdbId):
        self.movieId = movieId
        self.imdbId = imdbId
        self.tmdbId = tmdbId

    def __str__(self):
        return f"Movie ID: {self.movieId}, IMDB ID: {self.imdbId}, TMDB ID: {self.tmdbId}"