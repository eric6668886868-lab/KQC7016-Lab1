"""Offline functional tests for Lab1.py (do not require Internet)."""
import csv
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from Lab1 import Country, extract_countries, run, robots_permission, SOURCE_URL  # noqa: E402

FIXTURE = Path(__file__).with_name("sample_countries.html")


def test_parse_realistic_html():
    rows = extract_countries(FIXTURE.read_text(encoding="utf-8"))
    assert len(rows) == 5
    assert rows[0] == Country("Andorra", "Andorra la Vella", 84000, 468.0)
    assert rows[3].population == 0
    assert rows[3].area_km2 == 14_000_000.0
    assert rows[4].name == "China"


def test_csv_exports_and_filter(tmp_path):
    data = run(FIXTURE.read_text(encoding="utf-8"), tmp_path)
    assert len(data["filtered"]) == 2
    for filename, count in [("countries_all.csv", 5), ("countries_population_10m_plus.csv", 2), ("countries_top10_population.csv", 5)]:
        with (tmp_path / filename).open(encoding="utf-8-sig", newline="") as file:
            assert len(list(csv.DictReader(file))) == count


def test_broken_html_rejected():
    with pytest.raises(ValueError):
        extract_countries("<html><body>No cards</body></html>")
    with pytest.raises(ValueError):
        extract_countries("<div class='country'><h3 class='country-name'>Broken</h3></div>")


class Response:
    def __init__(self, code, content):
        self.status_code, self.text = code, content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ValueError("HTTP error")

class Session:
    def __init__(self, response):
        self.response = response

    def get(self, *args, **kwargs):
        return self.response


def test_robots_permission_allow_and_disallow():
    response = Response(200, "User-agent: *\nDisallow: /lessons/\nDisallow: /faq/\n")
    assert robots_permission(Session(response), SOURCE_URL)[0] is True
    assert robots_permission(Session(response), "https://www.scrapethissite.com/lessons/")[0] is False



def test_unicode_names_preserved():
    html = """<html><div class='country'><h3 class='country-name'><i></i>Åland</h3>
       <span class='country-capital'>Mariehamn</span>
       <span class='country-population'>26,711</span>
       <span class='country-area'>1.58E3</span></div></html>"""
    assert extract_countries(html) == [Country("Åland", "Mariehamn", 26711, 1580.0)]


def test_duplicate_names_rejected():
    html = FIXTURE.read_text(encoding="utf-8")
    first_card = html.split('<div class="country">')[1].split('</div>')[0]
    dup = html.replace('</body>', f'<div class="country">{first_card}</div></body>')
    with pytest.raises(ValueError, match="Duplicate"):
        extract_countries(dup)


def test_negative_population_rejected():
    html = FIXTURE.read_text(encoding="utf-8").replace('84000', '-84000', 1)
    with pytest.raises(ValueError, match="Invalid values"):
        extract_countries(html)


def test_invalid_area_rejected():
    html = FIXTURE.read_text(encoding="utf-8").replace('468.0', 'unknown', 1)
    with pytest.raises(ValueError, match="invalid data"):
        extract_countries(html)


def test_filter_threshold_boundary(tmp_path):
    base_html = FIXTURE.read_text(encoding="utf-8")
    html = base_html.replace('29121286', '10000000', 1)
    records = run(html, tmp_path)
    assert len(records['filtered']) == 2
    assert any(r.population == 10_000_000 for r in records['filtered'])
    assert records['top_ten'][0].name == 'China'


def test_web_permission_rejects_forbidden_path():
    response = Response(200, 'User-agent: *\nDisallow: /pages/\n')
    assert robots_permission(Session(response), SOURCE_URL)[0] is False


def test_robots_404_means_no_robots_file():
    response = Response(404, '')
    assert robots_permission(Session(response), SOURCE_URL)[0] is True


def test_large_synthetic_html_keeps_all_records(tmp_path):
    card = "<div class='country'><h3 class='country-name'>Country {n}</h3>" \
           "<span class='country-capital'>Capital {n}</span>" \
           "<span class='country-population'>{pop}</span>" \
           "<span class='country-area'>100.5</span></div>"
    html = '<html><body>' + ''.join(card.format(n=i, pop=1_000_000+i*200_000) for i in range(250)) + '</body></html>'
    data = run(html, tmp_path)
    assert len(data['records']) == 250
    assert len(data['filtered']) == len([i for i in range(250) if 1_000_000+i*200_000 >= 10_000_000])
    assert len(data['top_ten']) == 10
