"""Small pure text helpers for Signal agent modules."""


def truncate_text(text: str | None, max_chars: int = 500, suffix: str = "...") -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    cut = max(0, max_chars - len(suffix))
    return text[:cut] + suffix
