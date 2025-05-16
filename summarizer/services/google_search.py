import re

import requests

from summarizer.config import GOOGLE_SEARCH_API_KEY, GOOGLE_CSE_ID


def fetch_news(entity):
    params = {
        "q": f"{entity} latest legal news and issues",
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": 10
    }
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        data = response.json()
        return [{"title": item["title"], "link": item["link"]} for item in data.get("items", [])]
    except:
        return []


def fetch_documents(entity):
    params = {
        "q": f"{entity} (\"annual report\" OR \"financial report\") filetype:pdf",
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": 10
    }

    docs = []
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
        response.raise_for_status()
        items = response.json().get("items", [])
    except Exception as e:
        return []

    for item in items:
        title = item.get("title", "Untitled Document")
        link = item.get("link", "")
        year_match = re.search(r"(20\d{2})", title) or re.search(r"(20\d{2})", link)
        year = year_match.group(1) if year_match else "Unknown"

        docs.append({
            "title": title,
            "link": link,
            "year": year
        })

    docs.sort(key=lambda d: int(d["year"]) if d["year"].isdigit() else 0, reverse=True)
    return docs[:5]
