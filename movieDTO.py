class Movie:
    def __init__(self, movie_id, title, genre):
        self.id = movie_id
        self.title = title
        self.genre = genre

    def __repr__(self):
        return (
            f"Movie(id={self.id}, title={self.title}, "
            f"genre={self.genre})"
        )