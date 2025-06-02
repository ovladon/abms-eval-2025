# sanitize_utils.py
import bleach

def sanitize_input(user_input: str) -> str:
    """
    Sanitize text input to remove potential harmful content.
    """
    return bleach.clean(user_input)

