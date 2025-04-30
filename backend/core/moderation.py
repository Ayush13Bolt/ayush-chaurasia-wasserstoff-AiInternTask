import re
from typing import List

# Using a  list
BAD_WORDS: List[str] = [
    r"\b(damn|hell|crap)\b",  # r"\b" for word boundary
    r"ass\w+",
    r"fuck\w+",  
    r"shit\w+",  # Match words starting with "shit"
    # Add more patterns as needed
]

def moderate_input(text: str) -> bool:
    """
    Checks if the input text contains any bad words, using more robust techniques.
    True if the text is clean, False otherwise.
    """
    lowered_text = text.lower()  # keep lowercasing
    for pattern in BAD_WORDS:
        if re.search(pattern, lowered_text):
            return False
    return True
