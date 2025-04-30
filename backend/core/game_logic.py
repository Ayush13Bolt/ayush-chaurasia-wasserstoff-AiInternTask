from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse  # Import JSONResponse
from backend.core.ai_client import ask_ai_async
from threading import Lock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.models import GuessCount
from backend.db.db import get_db

# Lock for thread-safe access to global guess counts
global_guess_counts_lock = Lock()
seed_word = "rock".lower()  # Initial seed word

# Fetch how many times a word has been guessed globally
async def get_global_guess_count(db: AsyncSession, word: str) -> int:
    with global_guess_counts_lock:
        stmt = select(GuessCount).where(GuessCount.word == word)  # Construct the select statement
        result = await db.execute(stmt)  # Execute the statement
        db_guess_count = result.scalar_one_or_none()  # Get the result
        if db_guess_count:
            return db_guess_count.count
        return 0

# Increment the global guess count for a word
async def increment_global_guess_count(db: AsyncSession, word: str):
    with global_guess_counts_lock:
        stmt = select(GuessCount).where(GuessCount.word == word)  # Construct select.
        result = await db.execute(stmt)
        db_guess_count = result.scalar_one_or_none()
        if db_guess_count:
            db_guess_count.count += 1
        else:
            new_guess_count = GuessCount(word=word, count=1)
            db.add(new_guess_count)
        await db.commit()

# Core logic to handle a user’s guess and process game state
async def process_guess(app: FastAPI, user_id: str, guess: str, persona: str, user_sessions: dict, user_sessions_lock: Lock, db: AsyncSession = Depends(get_db)):
    guess_lower = guess.lower()
    with user_sessions_lock:
        if guess_lower in user_sessions[user_id]["guessed_words"]:
            # Game Over condition: repeated word
            user_sessions[user_id] = {"history": [(seed_word.capitalize(), "seed")], "guessed_words": set(), "score": 0, "current_word": seed_word}
            global_count = await get_global_guess_count(db, guess_lower)
            return JSONResponse(content={  # Changed to JSONResponse
                "game_over": True,
                "message": f"GAME OVER! ❌! You have already used the word '{guess}' before. {verdict.lower()}",
                "verdict": "NO",
                "global_guess_count": global_count
            })

        # Get the word to beat from the session, default to seed_word if no successful guess yet
        word_to_beat = user_sessions[user_id].get("current_word", seed_word)

        # Ask AI whether the guess beats the current word
        verdict = await ask_ai_async(word_to_beat, guess, persona)

        if "YES" in verdict:
            # Valid guess: update session with new progress
            user_sessions[user_id]["guessed_words"].add(guess_lower)
            user_sessions[user_id]["history"].append((guess, "correct"))
            user_sessions[user_id]["score"] += 1
            # Update the current_word to the successful guess
            user_sessions[user_id]["current_word"] = guess_lower

            await increment_global_guess_count(db, guess_lower)
            global_count = await get_global_guess_count(db, guess_lower)

            return JSONResponse(content={  # Changed to JSONResponse
                "verdict": "YES",
                "message": f"✅ Nice! “{guess}” beats “{word_to_beat}”. {verdict.lower()}",
                "global_guess_count": global_count,
                "score": user_sessions[user_id]["score"]
            })
        else:
            # Game Over condition: AI says "NO"
            user_sessions[user_id] = {"history": [(seed_word.capitalize(), "seed")], "guessed_words": set(), "score": 0, "current_word": seed_word}
            global_count = await get_global_guess_count(db, guess_lower)
            return JSONResponse(content={  # Changed to JSONResponse
                "game_over": True,
                "verdict": "NO",
                "message": f"GAME OVER! ❌! “{guess}” does not beat “{word_to_beat}”. {verdict.lower()}",
                "global_guess_count": global_count
            })

# Retrieve the list of guessed words for a user that exist in the database
async def get_history(app: FastAPI, user_id: str, user_sessions: dict, user_sessions_lock: Lock, db: AsyncSession = Depends(get_db)):
    with user_sessions_lock:
        stmt = select(GuessCount.word).where(GuessCount.word.in_(user_sessions[user_id]["guessed_words"]))  # Construct select
        result = await db.execute(stmt)  # Execute statement.
        guessed_words = [row[0] for row in result.all()]
        return guessed_words

from fastapi import Depends  # Ensure Depends is imported here
from backend.db.db import get_db  # Ensure get_db is imported here
