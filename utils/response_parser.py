import json


def clean_message(raw: str) -> str:
    """
    Remove code fences and surrounding whitespace from raw message text.
    """
    msg = raw.strip()
    # Remove markdown code fences
    if msg.startswith('```json'):
        msg = msg[len('```json'):].lstrip()
    elif msg.startswith('```'):
        msg = msg[len('```'):].lstrip()
    if msg.endswith('```'):
        msg = msg[:-len('```')].rstrip()
    return msg


def is_json_message(raw: str) -> bool:
    """
    Determine if the cleaned message text is valid JSON (object or array).
    """
    cleaned = clean_message(raw)
    return cleaned.startswith('{') or cleaned.startswith('[')


def parse_json_message(raw: str):
    """
    Parse the cleaned raw message as JSON and return the resulting object.
    """
    cleaned = clean_message(raw)
    return json.loads(cleaned) 