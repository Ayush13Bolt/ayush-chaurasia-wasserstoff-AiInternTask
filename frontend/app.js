document.addEventListener('DOMContentLoaded', () => {
    // Get references to all necessary DOM elements
    const guessInput = document.getElementById('guessInput');
    const submitGuess = document.getElementById('submitGuess');
    const feedback = document.getElementById('feedback');
    const scoreDisplay = document.getElementById('score');
    const globalGuessCountDisplay = document.getElementById('globalGuessCount');
    const lastFiveGuessesList = document.getElementById('lastFiveGuesses');
    const requestHistoryButton = document.getElementById('requestHistory');
    const fullHistoryList = document.getElementById('fullHistory');

    let guesses = [];
    let score = 0;

    // Update the list showing the last five guesses made
    function updateLastFiveGuesses() {
        lastFiveGuessesList.innerHTML = '';
        const recentGuesses = guesses.slice(-5);
        recentGuesses.forEach(guess => {
            const listItem = document.createElement('li');
            listItem.textContent = guess;
            lastFiveGuessesList.appendChild(listItem);
        });
    }

    // Reset all game-related UI elements
    function resetGameDisplay() {
        score = 0;
        guesses = [];
        scoreDisplay.textContent = `Score: ${score}`;
        lastFiveGuessesList.innerHTML = '';
        globalGuessCountDisplay.textContent = `Zero Rounds Played.`;
        feedback.textContent = '';
        feedback.classList.remove('game-over');
        fullHistoryList.style.display = 'none';
        fullHistoryList.innerHTML = '';
    }

    // Handle the logic when a guess is submitted
    async function submitGuessHandler() {
        const guess = guessInput.value.trim();

        if (guess) {
            try {
                // Send the guess to the backend with the selected persona
                const response = await fetch(`/guess?guess=${guess}&persona=cheery`, {
                    method: 'POST',
                });

                const data = await response.json();

                if (response.ok) {
                    // Handle correct guess
                    if (data.verdict === 'YES') {
                        feedback.textContent = data.message;
                        score++;
                        scoreDisplay.textContent = `Score: ${score}`;
                        guesses.push(guess);
                        updateLastFiveGuesses();

                        // Show global guess count if available
                        if (data.global_guess_count !== undefined) {
                            globalGuessCountDisplay.textContent = `Total Guesses for "${guess}" : ${data.global_guess_count}`;
                        } else {
                            globalGuessCountDisplay.textContent = `Zero Rounds Played.`;
                        }

                        feedback.classList.add('correct');
                        setTimeout(() => feedback.classList.remove('correct'), 1000);

                    // Handle game over condition
                    } else if (data.game_over) {
                        feedback.classList.add('game-over');

                        if (data.global_guess_count !== undefined) {
                            globalGuessCountDisplay.textContent = `Total Guesses for "${guess}" : ${data.global_guess_count}`;
                        } else {
                            globalGuessCountDisplay.textContent = `Zero Rounds Played`;
                        }

                        resetGameDisplay();
                        feedback.textContent = data.message;

                    // Handle incorrect guess
                    } else {
                        feedback.textContent = data.message;
                    }

                } else {
                    // Handle bad requests and other errors
                    if (response.status === 400) {
                        const errorData = await response.json();
                        feedback.textContent = errorData.detail || 'An error occurred.';
                    } else {
                        feedback.textContent = 'An unexpected error occurred.';
                    }
                }

            } catch (error) {
                // Catch network or profanity-related errors
                feedback.textContent = 'Use of Profane words is not allowed! Try again.';
            }

            // Clear input and hide full history after submission
            guessInput.value = '';
            updateLastFiveGuesses();
            fullHistoryList.style.display = 'none';
            fullHistoryList.innerHTML = '';
        }
    }

    // Fetch and display the full guess history from the server
    async function requestHistoryHandler() {
        const response = await fetch('/history');
        const data = await response.json();

        if (data.history && data.history.length > 0) {
            fullHistoryList.innerHTML = '';
            data.history.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = item;
                fullHistoryList.appendChild(listItem);
            });
            fullHistoryList.style.display = 'block';
        } else {
            fullHistoryList.innerHTML = '<li>No history available.</li>';
            fullHistoryList.style.display = 'block';
        }
    }

    // Attach event listeners to buttons for guess submission and history request
    submitGuess.addEventListener('click', submitGuessHandler);
    requestHistoryButton.addEventListener('click', requestHistoryHandler);
});
