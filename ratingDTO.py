class raitingDTO:
    def __init__(self, userId, movieId, rating, timestamp):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
        self.timestamp = timestamp
    def __str__(self):
        return f"User {self.userId} rated movie {self.movieId} with {self.rating} at {self.timestamp}"