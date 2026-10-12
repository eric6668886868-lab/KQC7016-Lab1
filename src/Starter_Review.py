"""Independent walkthrough of the lecturer's original Lab1.py exercise.

This file is a learning aid, not a reproduction of a teammate's work.
It shows the HTTP request, parser, elements and Python keyword filtering.
"""
import requests
from bs4 import BeautifulSoup

URL = "https://realpython.github.io/fake-jobs/"


def main():
    response = requests.get(URL, timeout=20)
    response.raise_for_status()
    print("PART 1 - HTTP FETCH")
    print("URL:", URL)
    print("HTTP status:", response.status_code)
    print("HTML length:", len(response.content))

    soup = BeautifulSoup(response.text, "html.parser")
    print("\nPART 2 - HTML PARSING")
    print("Page title:", soup.title.get_text(strip=True) if soup.title else "Not found")

    container = soup.find(id="ResultsContainer")
    if container is None:
        raise ValueError("ResultsContainer was not found; site layout may have changed")
    cards = container.select("div.card-content")
    print("\nPART 3 - LOCATION OF JOB CARDS")
    print("Number of jobs:", len(cards))

    print("\nPART 4 - SAMPLE FIELDS (FIRST THREE JOBS)")
    for card in cards[:3]:
        title = card.select_one("h2.title")
        company = card.select_one("h3.company")
        location = card.select_one("p.location")
        print("Title:", title.get_text(strip=True) if title else "")
        print("Company:", company.get_text(strip=True) if company else "")
        print("Location:", location.get_text(strip=True) if location else "")
        print("-")

    matches = []
    for card in cards:
        title = card.select_one("h2.title")
        if title and "python" in title.get_text(" ", strip=True).lower():
            matches.append(title.get_text(" ", strip=True))
    print("\nPART 5 - CASE-INSENSITIVE TITLE FILTER")
    print("Python-related jobs:", len(matches))
    for title in matches:
        print("  ", title)


if __name__ == "__main__":
    main()
