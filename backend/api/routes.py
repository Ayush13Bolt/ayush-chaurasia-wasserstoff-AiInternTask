from fastapi import APIRouter, Request, HTTPException, Query, Response, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from backend.core.game_logic import process_guess
from backend.core.moderation import moderate_input
from backend.db.db import engine, get_db  

import uuid
from threading import Lock

router = APIRouter()

# Dictionary to store user sessions
user_sessions = {}
user_sessions_lock = Lock()

# Initial word to start the game
seed_word = "rock".lower()


@router.post("/guess")
async def make_guess(
    response: Response,
    request: Request,
    guess: str = Query(...),
    persona: str = Query("serious"),
    db_engine=Depends(get_db)
):
    # Try to fetch existing user_id from cookies
    user_id = request.cookies.get("user_id")

    with user_sessions_lock:
        # If no user_id, create new session and assign user_id
        if not user_id:
            user_id = str(uuid.uuid4())
            response.set_cookie(key="user_id", value=user_id, httponly=True)
            user_sessions[user_id] = {
                "history": [(seed_word.capitalize(), "seed")],
                "guessed_words": set(),
                "score": 0,
                "current_word": seed_word
            }
        # If cookie exists but session is missing, reinitialize session
        elif user_id not in user_sessions:
            user_sessions[user_id] = {
                "history": [(seed_word.capitalize(), "seed")],
                "guessed_words": set(),
                "score": 0,
                "current_word": seed_word
            }

    # Clean up the guess input
    guess = guess.strip()

    # Block the request if it contains profane words
    if not moderate_input(guess):
        return JSONResponse(
            status_code=400,
            content={"detail": "Use of Profane words is not allowed! Try again."}
        )

    # Process the guess using game logic
    result = await process_guess(
        request.app,
        user_id,
        guess,
        persona,
        user_sessions,
        user_sessions_lock,
        db_engine
    )
    return result


@router.get("/history")
async def get_guess_history(request: Request):
    # Get user_id from cookies
    user_id = request.cookies.get("user_id")

    with user_sessions_lock:
        # If session not found, return error
        if not user_id or user_id not in user_sessions:
            raise HTTPException(status_code=400, detail="No active game session")

        # Retrieve guess history for user
        history = user_sessions[user_id]["history"]

    # Return only actual guesses, skipping the seed word
    return {"history": [item[0] for item in history if item[1] != "seed"]}


@router.post("/reset")
async def reset_game_state(response: Response, request: Request):
    # Get user_id from cookies
    user_id = request.cookies.get("user_id")

    with user_sessions_lock:
        # If session exists, delete it
        if user_id in user_sessions:
            del user_sessions[user_id]

    # Remove the user_id cookie to fully reset session
    response.delete_cookie(key="user_id")
    return {"message": "Game session reset successfully"}
