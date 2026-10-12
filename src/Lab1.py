"""KQC7016 Lab 1: original web-scraping exercise (Semester 1, 2026/2027).

Prepared for MENG YIQUN (25064319), with AI coding assistance.
Target: Scrape This Site, public web-scraping practice sandbox.
The site's demographic values are a fixed educational sample, NOT current statistics.

Usage:
    python Lab1.py
    python Lab1.py --html-file tests/sample_countries.html  # offline parser test
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.scrapethissite.com/pages/simple/"
USER_AGENT = "KQC7016-Educational-WebScraper/1.0 (non-commercial classroom exercise)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 20
POPULATION_THRESHOLD = 10_000_000


@dataclass(frozen=True)
class Country:
    name: str
    capital: str
    population: int
    area_km2: float


def robots_permission(session: requests.Session, target_url: str) -> tuple[bool, str]:
    """Read the website's robots.txt before fetching its HTML page.

    A 404 means no robots file was provided; any other request failure stops the
    crawler rather than silently bypassing the site's instructions.
    """
    site = urlsplit(target_url)
    robots_url = f"{site.scheme}://{site.netloc}/robots.txt"
    response = session.get(robots_url, headers=HEADERS, timeout=TIMEOUT)
    if response.status_code == 404:
        return True, "No robots.txt file (HTTP 404)."
    response.raise_for_status()
    robot = RobotFileParser()
    robot.parse(response.text.splitlines())
    allowed = robot.can_fetch(USER_AGENT, target_url)
    return allowed, f"Read {robots_url}; allowed={allowed}"


def fetch_html(session: requests.Session, target_url: str = SOURCE_URL) -> str:
    allowed, message = robots_permission(session, target_url)
    print("Robots check:", message)
    if not allowed:
        raise PermissionError(f"robots.txt prohibits accessing {target_url}")
    response = session.get(target_url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = "utf-8"  # This teaching page declares UTF-8; preserve accented names.
    print(f"HTTP response: {response.status_code} ({len(response.content):,} bytes)")
    return response.text


def extract_countries(html_text: str) -> list[Country]:
    """Parse each country card into a validated structured record."""
    soup = BeautifulSoup(html_text, "html.parser")
    cards = soup.select("div.country")
    if not cards:
        raise ValueError("No country cards found; the HTML layout may have changed.")

    records: list[Country] = []
    for number, card in enumerate(cards, start=1):
        try:
            name = card.select_one("h3.country-name").get_text(" ", strip=True)
            capital = card.select_one("span.country-capital").get_text(" ", strip=True)
            pop_text = card.select_one("span.country-population").get_text(strip=True)
            area_text = card.select_one("span.country-area").get_text(strip=True)
            country = Country(name, capital, int(pop_text.replace(",", "")), float(area_text))
        except (AttributeError, ValueError) as exc:
            raise ValueError(f"Card {number} has incomplete/invalid data: {exc}") from exc
        if not country.name or country.population < 0 or country.area_km2 < 0:
            raise ValueError(f"Invalid values in card {number}: {country}")
        records.append(country)
    names = [record.name for record in records]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate country names found: cannot export reliably.")
    return records


def export_csv(records: list[Country], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Country", "Capital", "Population", "Area_km2"])
        for item in records:
            writer.writerow([item.name, item.capital, item.population, item.area_km2])


def run(html_text: str, output_dir: Path) -> dict[str, object]:
    records = extract_countries(html_text)
    filtered = [r for r in records if r.population >= POPULATION_THRESHOLD]
    top_ten = sorted(records, key=lambda r: (-r.population, r.name))[:10]

    export_csv(records, output_dir / "countries_all.csv")
    export_csv(filtered, output_dir / "countries_population_10m_plus.csv")
    export_csv(top_ten, output_dir / "countries_top10_population.csv")

    print("\n=== DATA EXTRACTION ===")
    print(f"Country / territory records: {len(records)}")
    print("First 5 records:")
    for record in records[:5]:
        print(f"  {record.name} | {record.capital} | {record.population:,} | {record.area_km2:g} km2")

    print("\n=== FILTERING AND SUMMARY ===")
    print(f"Population >= {POPULATION_THRESHOLD:,}: {len(filtered)} records")
    print(f"Zero-population entries: {sum(r.population == 0 for r in records)}")
    print("Top 10 populations (demo-site historical sample, NOT current figures):")
    for index, record in enumerate(top_ten, start=1):
        print(f"  {index:>2}. {record.name:25} {record.population:>15,}")
    print("\n=== SAVED FILES ===")
    for name in ("countries_all.csv", "countries_population_10m_plus.csv", "countries_top10_population.csv"):
        print(f"  {output_dir / name}")
    return {"records": records, "filtered": filtered, "top_ten": top_ten}


def main() -> int:
    parser = argparse.ArgumentParser(description="KQC7016 Lab 1 independent country-page web scraper")
    parser.add_argument("--html-file", type=Path, help="Local HTML file for offline parser verification")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    try:
        if args.html_file:
            print(f"MODE: OFFLINE HTML parser test using {args.html_file}")
            html_text = args.html_file.read_text(encoding="utf-8")
        else:
            print("MODE: LIVE HTTP website fetch")
            with requests.Session() as session:
                html_text = fetch_html(session)
        run(html_text, args.output_dir)
        return 0
    except (requests.RequestException, OSError, ValueError, PermissionError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
