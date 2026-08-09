"""
research_topic.py — fact-grounding step.

LLMs occasionally state incorrect exercise/anatomy claims confidently
(hallucination). Before the script-writing step, we pull a short factual
snippet from Wikipedia about the relevant muscle group / exercise concept
and hand that to the LLM as grounding notes — it's told to use these
facts rather than invent its own.
"""

import requests

WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
HEADERS = {"User-Agent": "HomeFitDaily-Research/1.0 (contact: none)"}


def _wiki_search_title(query):
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 1,
        "namespace": 0,
        "format": "json",
    }
    resp = requests.get(WIKI_SEARCH, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data[1]
    return results[0] if results else None


def research_topic(topic: str) -> str:
    """Returns a short factual grounding paragraph, or an empty string if unavailable."""
    try:
        title = _wiki_search_title(topic)
        if not title:
            print(f"[research_topic] No Wikipedia match for '{topic}'")
            return ""
        resp = requests.get(WIKI_SUMMARY.format(title=title.replace(" ", "_")), headers=HEADERS, timeout=10)
        resp.raise_for_status()
        summary = resp.json().get("extract", "")
        print(f"[research_topic] Grounded on Wikipedia page: {title}")
        return summary
    except Exception as e:
        print(f"[research_topic] Wikipedia lookup failed (non-fatal): {e}")
        return ""


if __name__ == "__main__":
    print(research_topic("Squat (exercise)"))
