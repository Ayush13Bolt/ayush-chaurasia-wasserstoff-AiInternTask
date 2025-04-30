import os
import google.generativeai as genai
from tenacity import retry, wait_exponential, stop_after_attempt
import asyncio
import logging

# Persona templates to guide AI responses in different tones
PERSONAS = {
    "serious": "As a strict, serious judge, carefully determine if the guess truly beats the seed word. Respond only with 'YES' or 'NO'.",
    "cheery": "As a fun, enthusiastic host, decide if the guess beats the seed word! Respond with 'YES' or 'NO' in a cheerful way."
}

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize and return the Gemini AI client
def initialize_ai_client():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. The AI functionality will not work.")
    genai.configure(api_key=gemini_api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

# Instantiate the AI model
model = initialize_ai_client()

# Retry logic to handle transient API failures
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5)
)
def ask_ai(word, guess, persona):
    # Construct the prompt with selected persona
    prompt = f"Does the word '{guess}' beat the word '{word}' logically, creatively, or realistically. Answer should be based on general knowledge or plausible reasoning, starting with 'YES' or 'NO' followed by a very short one line reasoning"
    contents = [
        {
            "role": "user",
            "parts": [
                {"text": f"{PERSONAS.get(persona, PERSONAS['serious'])} {prompt}"},
            ]
        }
    ]

    # Define safety filters for the AI response
    safety_settings = [
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    try:
        # Send request to Gemini model
        response = model.generate_content(
            contents,
            safety_settings=safety_settings
        )

        # Log full response for debugging
        logger.info(f"Full Gemini API Response: {response}")

        # Check if response was blocked for safety reasons
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            raise Exception(f"Gemini API blocked the request: {response.prompt_feedback.block_reason}")

        logger.info(f"Raw response: {response}")

        # Validate the AI's completion status
        finish_reason = response.candidates[0].finish_reason
        logger.info(f"Finish reason: {finish_reason} (type: {type(finish_reason)})")

        if finish_reason != 1:
            raise Exception(f"Gemini API did not complete the generation successfully: {finish_reason}")

        # Extract and validate the actual AI response
        if response.text:
            full_text = response.text.strip().upper()
            logger.info(f"Full response text: '{full_text}'")

            # Return verdict only if it contains YES or NO
            if "YES" in full_text:
                verdict = full_text
                return verdict
            elif "NO" in full_text:
                verdict = full_text
                return verdict
            else:
                raise ValueError(f"Gemini API returned an unexpected verdict: '{full_text}'. Could not find 'YES' or 'NO'.")
        else:
            raise ValueError("Gemini API returned an empty response text.")
    except Exception as e:
        # Log and raise error if any part of the process fails
        logger.error(f"Gemini API error: {e}")
        raise

# Wrapper to run the ask_ai function asynchronously
async def ask_ai_async(seed, guess, persona):
    return await asyncio.to_thread(ask_ai, seed, guess, persona)
