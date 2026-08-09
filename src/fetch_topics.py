"""
fetch_topics.py — topic research step.

Pulls hot post titles from a few fitness-focused subreddits (no API key
needed for read-only Reddit JSON endpoints), scores each title against
config.yaml's keyword-boost list, and returns the best-scoring one. Falls
back to a rotating static list if Reddit is unreachable (rate limits /
blocks happen — this keeps the pipeline running instead of crashing).
"""

from datetime import date

import requests
import yaml

HEADERS = {"User-Agent": "HomeFitDaily-TopicResearch/1.0"}


def _load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def fetch_reddit_titles(subreddits):
    titles = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=15"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for post in data["data"]["children"]:
                titles.append(post["data"]["title"])
        except Exception as e:
            print(f"[fetch_topics] Reddit fetch failed for r/{sub}: {e}")
    return titles


def score_topic(title, keywords_boost):
    title_lower = title.lower()
    score = 0
    for word in keywords_boost:
        if word.lower() in title_lower:
            score += 3
    return score


def get_best_topic():
    config = _load_config()
    filt = config["topic_filter"]

    all_titles = fetch_reddit_titles(filt["subreddits"])

    if all_titles:
        scored = [(score_topic(t, filt["keywords_boost"]), t) for t in all_titles]
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_title = scored[0]
        if best_score > 0:
            print(f"[fetch_topics] Picked from Reddit (score {best_score}): {best_title}")
            return best_title

    # Fallback: rotate through the static list by day-of-year so it still
    # cycles through variety even when Reddit gives nothing useful.
    fallback = filt["fallback_topics"]
    topic = fallback[date.today().timetuple().tm_yday % len(fallback)]
    print(f"[fetch_topics] Using fallback topic: {topic}")
    return topic


if __name__ == "__main__":
    print(get_best_topic())
