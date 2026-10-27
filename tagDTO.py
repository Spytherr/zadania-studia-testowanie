class tagDTO:
    def __init__(self,userId,movieId,tag,timestamp):
        self.userId = userId
        self.movieId = movieId
        self.tag = tag
        self.timestamp = timestamp

    def __str__(self):
        return f"User {self.userId} tagged movie {self.movieId} with '{self.tag}' at {self.timestamp}"