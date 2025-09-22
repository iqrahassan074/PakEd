import re

BANNED_WORDS = {"cheat", "answer key", "paper leak"}

def input_allowed(text: str) -> tuple[bool, str]:
    t = text.lower()
    for w in BANNED_WORDS:
        if w in t:
            return False, f"Request contains banned word: {w}"
    if len(text.strip()) == 0:
        return False, "Empty question."
    if len(text) > 2000:
        return False, "Question too long—make it shorter."
    return True, ""

def sanitize_output(text: str) -> str:
    # minimal sanitization — strip weird control chars
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text).strip()
