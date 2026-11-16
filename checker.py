import requests


def check_text(text, lang="en-US"):
    """Return (corrected_text, list_of_changes). If LanguageTool is unavailable,
    return the original text unchanged."""
    try:
        r = requests.post(
            "https://api.languagetool.org/v2/check",
            data={"text": text, "language": lang},
            timeout=10,
        )
        r.raise_for_status()
        matches = r.json().get("matches", [])
    except Exception:
        return text, []

    changes = []
    for m in sorted(matches, key=lambda m: m["offset"], reverse=True):
        if not m["replacements"]:
            continue
        start, end = m["offset"], m["offset"] + m["length"]
        old, new = text[start:end], m["replacements"][0]["value"]
        text = text[:start] + new + text[end:]
        changes.append(f'"{old}" → "{new}" ({m["message"]})')
    return text, list(reversed(changes))