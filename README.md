# KQC7016 Data Analytics - Lab 1: Independent Web Scraping Exercise

**Student:** MENG YIQUN (25064319)  
**Term:** Semester 1, Session 2026/2027  
**Project:** Countries of the World - Web Scraping (new implementation)

## What this project does

1. Reviews the lecturer's original Real Python `fake-jobs` example in five stages (`Starter_Review.py`).
2. Independently scrapes a different public training website, [Scrape This Site - Countries](https://www.scrapethissite.com/pages/simple/) (`Lab1.py`).
3. Checks `robots.txt` before requesting the page; rejects a prohibited path.
4. Extracts country/territory name, capital, sample population and sample area using BeautifulSoup.
5. Filters entries with sample population >= 10,000,000, lists the ten largest values and saves three CSV files.

**Important:** This is a deliberately static educational example. The population figures are **not current country statistics**. Do not use them for real demographic claims.

## Run on Windows

Open Terminal/PowerShell in the extracted folder and run:

```powershell
python -m pip install -r src/requirements.txt
python src/Lecturer_Lab1_Reference.py
python src/Starter_Review.py
python src/Lab1.py
```

The main program will create an `outputs/` folder with:

- `countries_all.csv`
- `countries_population_10m_plus.csv`
- `countries_top10_population.csv`

It requires an Internet connection to fetch the site and check `robots.txt`.

## Offline verification (available even without Internet)

```powershell
python src/Lab1.py --html-file tests/sample_countries.html --output-dir outputs_sample
python -m pip install -r src/requirements-dev.txt
python -m pytest -q tests/test_lab1.py
```

The offline fixture contains only five cards and should **not** be mistaken for the live 250-card result.

## Site permission

The website's `robots.txt` was reviewed when this project was prepared. The rules disallowed `/lessons/` and `/faq/` only, not `/pages/simple/`. `Lab1.py` checks the live `robots.txt` again on each run. Stop if the site's policy changes or access is blocked.

## Submission notes

This repository should contain **code** and, optionally, sample output data. The corresponding Lab 1 report (DOCX/PDF) is submitted using the lecturer's SPeCTRUM course submission instructions, not necessarily through GitHub. Confirm the final repository URL and update the report before submitting.

## Acknowledgement

Run the lecturer original and the five-stage walkthrough before the modified script; save screenshots of genuine terminal outputs.

The original course example is stored as `src/Lecturer_Lab1_Reference.py` for comparison. The new country scraper and verification tests were developed independently. No previous student-team source code or screenshots were reused.
