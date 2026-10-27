class movieDetailsDTO:
    def __init__(self, title, director, genre):
        self.title = title
        self.director = director
        self.genre = genre

    def __str__(self):
        return f"{self.title} ({self.release_year}), directed by {self.director}, Genre: {self.genre}"