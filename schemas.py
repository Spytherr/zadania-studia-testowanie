from pydantic import BaseModel, Field


class MovieCreate(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    genres: str = Field(min_length=1, max_length=255)


class MovieResponse(BaseModel):
    id: int
    title: str
    genre: str


class RatingCreate(BaseModel):
    user_id: int = Field(gt=0)
    movie_id: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)
    timestamp: int = Field(gt=0)


class RatingResponse(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int


class LinkCreate(BaseModel):
    movieId: int = Field(gt=0)
    imdbId: str = Field(min_length=1, max_length=7)
    tmdbId: int | None = Field(default=None, gt=0)


class LinkResponse(BaseModel):
    movieId: int
    imdbId: str
    tmdbId: int | None


class TagCreate(BaseModel):
    userId: int = Field(gt=0)
    movieId: int = Field(gt=0)
    tag: str = Field(min_length=1, max_length=255)
    timestamp: int = Field(gt=0)


class TagResponse(BaseModel):
    id: int
    userId: int
    movieId: int
    tag: str
    timestamp: int
