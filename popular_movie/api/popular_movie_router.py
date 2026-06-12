from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from popular_movie.repository.popular_movie_repo import fetch_popular_movies

router = APIRouter()

class MovieResponse(BaseModel):
    movie_id: int
    title: str
    title_ko: Optional[str] = None
    genres: str
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None
    avg_rating: float
    click_count: int

@router.get("/popular", response_model=list[MovieResponse])
def get_popular_movies(limit: int = Query(default=10, le=50)):
    rows = fetch_popular_movies(limit)
    return [
        MovieResponse(
            movie_id=row[0],
            title=row[1],
            title_ko=row[2],
            genres=row[3],
            poster_path=row[4],
            vote_average=row[5],
            avg_rating=row[6],
            click_count=row[7],
        )
        for row in rows
    ]