
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.data_loader import load_users, load_subjects
from app.matcher import recommend_users


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="Peer Matching API",
    description="Peer learning recommendation system",
    version="1.0.0"
)


# =========================================================
# Request Models
# =========================================================

class UserInput(BaseModel):
    strengths: list[str]
    weaknesses: list[str]


# =========================================================
# Response Models
# =========================================================

class MatchResult(BaseModel):
    id: int
    name: str
    match_score: float
    quality: str
    can_learn: list[str]
    can_teach: list[str]
    reasons: list[str]


class RecommendationResponse(BaseModel):
    recommendations: list[MatchResult]


# =========================================================
# Helper Function
# =========================================================

def format_results(results):

    formatted_results = []

    for result in results:

        formatted_results.append({
            "id": result["id"],
            "name": result["name"],
            "match_score": round(result["score"], 2),
            "quality": result["quality"],
            "can_learn": result["user1_can_learn"],
            "can_teach": result["user2_can_learn"],
            "reasons": result["reasons"]
        })

    return formatted_results


# =========================================================
# Home
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Peer Matching API is running"
    }


# =========================================================
# Get Subjects
# =========================================================

@app.get("/subjects")
def get_subjects():

    subjects = load_subjects()

    return subjects


# =========================================================
# Recommend Users - New User
# =========================================================

@app.post(
    "/recommend",
    response_model=RecommendationResponse
)
def get_recommendations(data: UserInput):

    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------

    users = load_users()
    subjects = load_subjects()


    # -----------------------------------------------------
    # Create valid subject set
    # -----------------------------------------------------

    valid_subjects = set()

    for category in subjects.values():

        valid_subjects.update(category)


    # -----------------------------------------------------
    # Validate strengths
    # -----------------------------------------------------

    invalid_strengths = [
        subject
        for subject in data.strengths
        if subject not in valid_subjects
    ]


    # -----------------------------------------------------
    # Validate weaknesses
    # -----------------------------------------------------

    invalid_weaknesses = [
        subject
        for subject in data.weaknesses
        if subject not in valid_subjects
    ]


    # -----------------------------------------------------
    # Invalid subject error
    # -----------------------------------------------------

    if invalid_strengths or invalid_weaknesses:

        raise HTTPException(
            status_code=400,
            detail={
                "invalid_strengths": invalid_strengths,
                "invalid_weaknesses": invalid_weaknesses
            }
        )


    # -----------------------------------------------------
    # Same subject cannot be strength + weakness
    # -----------------------------------------------------

    common_subjects = (
        set(data.strengths) &
        set(data.weaknesses)
    )

    if common_subjects:

        raise HTTPException(
            status_code=400,
            detail=(
                "A subject cannot be both "
                "strength and weakness: "
                + ", ".join(common_subjects)
            )
        )


    # -----------------------------------------------------
    # Create temporary user
    # -----------------------------------------------------

    new_user = {
        "id": 0,
        "name": "New User",
        "strengths": data.strengths,
        "weaknesses": data.weaknesses
    }


    # -----------------------------------------------------
    # Find recommendations
    # -----------------------------------------------------

    results = recommend_users(
        new_user,
        users,
        min_score=50
    )


    # -----------------------------------------------------
    # Sort by highest score
    # -----------------------------------------------------

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )


    # -----------------------------------------------------
    # Return only Top 5
    # -----------------------------------------------------

    results = results[:5]


    # -----------------------------------------------------
    # Return formatted response
    # -----------------------------------------------------

    return {
        "recommendations": format_results(results)
    }


# =========================================================
# Recommend Users - Existing User
# =========================================================

@app.get(
    "/recommend/{user_id}",
    response_model=RecommendationResponse
)
def get_existing_user_recommendations(user_id: int):

    # -----------------------------------------------------
    # Load users
    # -----------------------------------------------------

    users = load_users()


    # -----------------------------------------------------
    # Check user exists
    # -----------------------------------------------------

    user_exists = any(
        user["id"] == user_id
        for user in users
    )

    if not user_exists:

        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )


    # -----------------------------------------------------
    # Find actual user
    # -----------------------------------------------------

    user = next(
        user
        for user in users
        if user["id"] == user_id
    )


    # -----------------------------------------------------
    # Find recommendations
    # -----------------------------------------------------

    results = recommend_users(
        user,
        users,
        min_score=50
    )


    # -----------------------------------------------------
    # Sort by highest score
    # -----------------------------------------------------

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )


    # -----------------------------------------------------
    # Return only Top 5
    # -----------------------------------------------------

    results = results[:5]


    # -----------------------------------------------------
    # Return formatted response
    # -----------------------------------------------------

    return {
        "recommendations": format_results(results)
    }

