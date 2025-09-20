# safety.py
import re

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life",
    "harm myself", "self harm", "hurting myself"
]

def detect_crisis(text: str) -> bool:
    lower = text.lower()
    for kw in CRISIS_KEYWORDS:
        if kw in lower:
            return True
    return False

def redact_pii(text: str) -> str:
    # simple PII redaction: emails, phones
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\d{10,}\b", "[REDACTED_PHONE]", text)
    return text
