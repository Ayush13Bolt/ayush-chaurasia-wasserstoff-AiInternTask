# Readme.md

# Word Chain Game - "WHAT BEATS ROCK"

1.  Game Description

    A simple word chain game where players try to find a word that "beats" the previous word, according to a Large Language Model (LLM). The LLM determines if a word "beats" another based on logical, creative, or realistic reasoning.

2.  Rules

    * The game starts with a seed word: "rock".
    * Players enter a word as a guess.
    * The LLM decides if the guess word "beats" the previous word.
    * A word "beats" another if it dominates other one.
    * The LLM responds with "YES" or "NO" and a short explanation.
    * If the LLM says "YES", the player's word becomes the new word to beat.
    * If the LLM says "NO", the game ends.
    * Players cannot repeat words.
    * The game continues until a player makes a guess that the LLM determines does not "beat" the previous word.

3.  How to Play

    * Start the game.
    * Enter a word in the guess input field.
    * Submit your guess.
    * The game will display the LLM's verdict (YES/NO) and explanation.
    * If YES, enter another word.
    * If NO, the game ends.
    * The goal is to create the longest possible valid word chain.

4.  Setup (From Dockerfile)

    The game is designed to be run using Docker. The Dockerfile sets up the following environment:

    * Base Image: `python:3.11-slim`
    * Working Directory: `/app`
    * Copies the application code (backend directory) into the container.
    * Installs system dependencies: `build-essential`, `libpq-dev`, `pkg-config`
    * Copies and installs Python dependencies from `requirements.txt`.
    * Creates a non-root user `myuser` and group, and switches to that user.
    * Defines environment variables:
        * `POSTGRES_USER`
        * `POSTGRES_PASSWORD`
        * `POSTGRES_DB`
        * `REDIS_HOST`
        * `REDIS_PORT`
        * `GEMINI_API_KEY` (Important:  You must set this)
    * Exposes port 8000.
    * Sets the command to run the application using `uvicorn`:
        `uvicorn backend.main:app --host 0.0.0.0 --port 8000`

    To run the game:

    1.  Ensure you have Docker installed.
    2.  Clone the repository.
    3.  Create a `.env` file in the root directory with the necessary environment variables (especially `GEMINI_API_KEY`).  Example:
        ```
        POSTGRES_USER=your_postgres_user
        POSTGRES_PASSWORD=your_postgres_password
        POSTGRES_DB=your_postgres_db
        REDIS_HOST=redis
        REDIS_PORT=6379
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY  # Get this from Google Cloud
        ```
    4.  Build the Docker image: `docker build -t word_chain_game .`
    5.  Run the Docker container using Docker Compose (recommended):
        ```bash
        docker-compose up
        ```
        or manually with docker:
        ```bash
        docker run -p 8000:8000 --env-file .env word_chain_game
        ```
    6.  The game will be accessible at `http://localhost:8000` in your browser.

5.  Architectural Choices

    * Backend:
        * Python framework: FastAPI
        * Asynchronous design using `asyncio`
        * Database: PostgreSQL (for storing guess counts)
        * Cache: Redis (for rate limiting and potentially other session data)
        * LLM Interaction: Google Gemini API
    * Frontend:
        * HTML, CSS, and JavaScript
        * Uses the Fetch API to communicate with the backend.
    * Containerization: Docker
    * Web Server: Uvicorn

    The architecture is a standard web application design, with a RESTful API backend, a dynamic frontend, and containerization for easy deployment.
    The backend uses FastAPI for its speed, asynchronous capabilities, and ease of use.  PostgreSQL is used for persistent data storage, and Redis is used as a fast, in-memory data store.
    The frontend is a simple web page that interacts with the backend API.

6.  Prompt Design

    The core of the game's logic relies on the prompt given to the LLM (Google Gemini). The prompt is designed to elicit a binary (YES/NO) response from the LLM, along with a short justification.

    Prompt:
    ```
    "Does the word '{guess}' beat the word '{word}' logically, creatively, or realistically. Answer should be based on general knowledge or plausible reasoning, starting with 'YES' or 'NO' followed by a very short one line reasoning"
    ```

    Key elements of the prompt:

    * Clear Question:  Asks if a word "beats" another.
    * Context: Provides the two words being compared (`{guess}` and `{word}`).
    * Criteria: Specifies the basis for comparison: "logically, creatively, or realistically."
    * Format:  Requires a specific output format: "YES/NO" followed by a short explanation.  This makes parsing the LLM's response easier.
    * Reasoning: Asks the LLM to provide a short one line reasoning.

    The prompt is designed to be concise and unambiguous, guiding the LLM towards providing a structured and usable response.  The use of "logically, creatively, or realistically" allows for a wider range of word relationships, making the game more interesting.
