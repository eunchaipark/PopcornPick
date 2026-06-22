from fastapi import APIRouter, HTTPException
from batch_recommendation.repository.rating_repo import fetch_user_rating, fetch_user_liked
from batch_recommendation.repository.recommendation_repo import fetch_recommendations, fetch_popular_fallback
from batch_recommendation.schema.recommendation import RecommendationItem, RecommendationResponse

router = APIRouter()


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations(user_id: int):
    rows = fetch_recommendations(user_id)

    if not rows:
        fallback = fetch_popular_fallback(20)
        if not fallback:
            raise HTTPException(status_code=404, detail="추천 결과가 없습니다.")
        return RecommendationResponse(
            user_id=user_id,
            recommendations=[RecommendationItem(**item) for item in fallback]
        )

    return RecommendationResponse(
        user_id=user_id,
        recommendations=[
            RecommendationItem(
                movie_id=row[0],
                title=row[1],
                title_ko=row[2],
                genres=row[3],
                poster_path=row[4],
                vote_average=row[5],
                score=row[6],
                rank=row[7],
            )
            for row in rows
        ]
    )


@router.get("/user-state/{user_id}/{movie_id}")
def get_user_movie_state(user_id: int, movie_id: int):
    rating = fetch_user_rating(user_id, movie_id)
    liked = fetch_user_liked(user_id, movie_id)
    return {"rating": rating, "liked": liked}
