"""Free, user-driven discovery helpers. No paid API and no scraping of search pages."""
from urllib.parse import quote_plus


def build_queries(keyword, wilaya="All Algeria", language="French"):
    keyword = (keyword or "").strip()
    if not keyword:
        return []
    location = "" if wilaya == "All Algeria" else f" {wilaya}"
    phrases = []
    if language in ("French", "French + Arabic"):
        phrases += [
            f'fournisseur {keyword}{location} Algérie',
            f'distributeur {keyword}{location} Algérie',
            f'grossiste {keyword}{location} Algérie',
            f'fabricant {keyword}{location} Algérie',
        ]
    if language in ("Arabic", "French + Arabic"):
        phrases += [
            f'مورد {keyword}{location} الجزائر',
            f'موزع {keyword}{location} الجزائر',
            f'مصنع {keyword}{location} الجزائر',
        ]
    return phrases


def build_search_links(query):
    """Return normal browser search URLs; the app does not scrape search-engine pages."""
    encoded = quote_plus(query)
    return [
        {"engine": "Google", "url": f"https://www.google.com/search?q={encoded}"},
        {"engine": "Bing", "url": f"https://www.bing.com/search?q={encoded}"},
        {"engine": "DuckDuckGo", "url": f"https://duckduckgo.com/?q={encoded}"},
    ]
