"""brasileirao_last5 - fetch last 5 matches per team for Brasileirão Série A

This script uses the football-data.org API. Set environment variable
`FOOTBALL_DATA_API_KEY` to your API key. If no key is provided the script
will try to use the bundled `sample_data.json` as fallback (for demo).
"""
from __future__ import annotations
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

import requests

# optional: Playwright-based scraper for JS-rendered pages
try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

COMP = "BSA"  # competition code for Campeonato Brasileiro Série A (football-data.org)
SEASON = "2025"


def fetch_json(url: str, headers: Dict[str, str] | None = None) -> Any:
    resp = requests.get(url, headers=headers or {})
    resp.raise_for_status()
    return resp.json()


def load_fallback_data() -> Dict[str, Any]:
    here = os.path.dirname(__file__)
    path = os.path.join(here, "sample_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_teams_and_matches(api_key: str | None) -> (List[Dict], List[Dict]):
    if not api_key:
        data = load_fallback_data()
        teams = data.get("teams", [])
        matches = data.get("matches", [])
        return teams, matches

    headers = {"X-Auth-Token": api_key}
    teams_url = f"https://api.football-data.org/v2/competitions/{COMP}/teams"
    matches_url = f"https://api.football-data.org/v2/competitions/{COMP}/matches?status=FINISHED"

    teams_data = fetch_json(teams_url, headers)
    matches_data = fetch_json(matches_url, headers)

    teams = teams_data.get("teams", [])
    matches = matches_data.get("matches", [])
    return teams, matches


def find_team_id(team_name="Flamengo", api_key: str | None = None) -> int | None:
    if not api_key:
        data = load_fallback_data()
        teams = data.get("teams", [])
        for t in teams:
            if team_name.lower() in (t.get("name") or "").lower():
                return t["id"]
        return None

    headers = {"X-Auth-Token": api_key}
    url = f"https://api.football-data.org/v2/competitions/{COMP}/teams"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    for t in r.json().get("teams", []):
        if team_name.lower() in (t.get("name") or "").lower():
            return t["id"]
    return None


def last_n_matches_for_team(team_id: int, matches: List[Dict], n: int = 5) -> List[Dict]:
    team_matches = []
    for m in matches:
        home = m.get("homeTeam") or {}
        away = m.get("awayTeam") or {}
        if home.get("id") == team_id or away.get("id") == team_id:
            team_matches.append(m)

    # sort descending by date
    team_matches.sort(key=lambda x: x.get("utcDate") or x.get("lastUpdated") or "", reverse=True)
    return team_matches[:n]


def format_match_for_team(m: Dict, team_id: int) -> str:
    utc = m.get("utcDate") or m.get("lastUpdated")
    try:
        date = datetime.fromisoformat(utc.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        date = utc or ""

    home = m.get("homeTeam", {})
    away = m.get("awayTeam", {})
    score = m.get("score", {})
    full = score.get("fullTime") or {}
    home_goals = full.get("homeTeam")
    away_goals = full.get("awayTeam")

    is_home = home.get("id") == team_id
    opponent = away.get("name") if is_home else home.get("name")
    venue = "Home" if is_home else "Away"

    score_text = "-"
    if home_goals is not None and away_goals is not None:
        score_text = f"{home_goals} x {away_goals}"

    return f"{date} | {venue} vs {opponent} | {score_text}"


def scrape_native_stats(team_id: int) -> (List[Dict], List[Dict]):
    """Attempt to scrape native-stats.org for the given team ID using Playwright.

    Returns (teams, matches) with minimal structure compatible with the script.
    """
    if sync_playwright is None:
        raise RuntimeError("Playwright not installed. Install with: pip install playwright ; then run: playwright install chromium")

    url = f"https://native-stats.org/team/{team_id}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Try to find structured rows
        selectors = [
            "table.matches tbody tr",
            "table tbody tr",
            ".matches-list .match",
            ".fixture-list .fixture",
            ".last10 .match",
        ]

        rows = []
        for sel in selectors:
            found = page.query_selector_all(sel)
            if found:
                rows = found
                break

        teams: List[Dict] = [{"id": team_id, "name": "Flamengo"}]
        matches: List[Dict] = []

        import re

        if rows:
            for r in rows[:20]:
                try:
                    text = r.inner_text()
                except Exception:
                    text = r.text_content() or ""

                date = None
                mdate = re.search(r"(\d{4}-\d{2}-\d{2})", text)
                if mdate:
                    date = mdate.group(1)

                mscore = re.search(r"(\d+)\s*[:xX\-]\s*(\d+)", text)
                if not mscore:
                    mscore = re.search(r"(\d+)\s+(\d+)", text)

                home = {"id": None, "name": None}
                away = {"id": None, "name": None}
                home_goals = None
                away_goals = None
                if mscore:
                    home_goals = int(mscore.group(1))
                    away_goals = int(mscore.group(2))
                    parts = re.split(r"\d+\s*[:xX\-]\s*\d+", text)
                    left = parts[0].strip() if parts else ""
                    right = parts[1].strip() if len(parts) > 1 else ""
                    home = {"id": team_id if "Flamengo" in left else None, "name": left}
                    away = {"id": team_id if "Flamengo" in right else None, "name": right}

                matches.append({
                    "utcDate": date,
                    "homeTeam": home,
                    "awayTeam": away,
                    "score": {"fullTime": {"homeTeam": home_goals, "awayTeam": away_goals}},
                })

        else:
            # fallback: try to find embedded JSON or parse visible text
            content = page.content()
            m = re.search(r'"matches"\s*:\s*(\[.*?\])', content, re.S)
            if m:
                import json

                try:
                    parsed = json.loads(m.group(1))
                    for item in parsed:
                        matches.append({
                            "utcDate": item.get("utcDate") or item.get("date"),
                            "homeTeam": item.get("homeTeam") or {"id": item.get("home_id"), "name": item.get("home")},
                            "awayTeam": item.get("awayTeam") or {"id": item.get("away_id"), "name": item.get("away")},
                            "score": {"fullTime": {"homeTeam": item.get("homeGoals"), "awayTeam": item.get("awayGoals")}},
                        })
                except Exception:
                    pass

            if not matches:
                text = page.inner_text("body")
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                for ln in reversed(lines):
                    if "Flamengo" in ln and re.search(r"\d+\s*[:xX]\s*\d+", ln):
                        sd = re.search(r"(\d{4}-\d{2}-\d{2})", ln)
                        date = sd.group(1) if sd else None
                        sc = re.search(r"(\d+)\s*[:xX]\s*(\d+)", ln)
                        if sc:
                            h = int(sc.group(1))
                            g = int(sc.group(2))
                            parts = ln.split("Flamengo")
                            left = parts[0].strip()
                            right = parts[1].strip() if len(parts) > 1 else ""
                            if left == "" or ln.startswith("Flamengo"):
                                home = {"id": team_id, "name": "Flamengo"}
                                away = {"id": None, "name": right}
                            else:
                                away = {"id": team_id, "name": "Flamengo"}
                                home = {"id": None, "name": left}
                            matches.append({
                                "utcDate": date,
                                "homeTeam": home,
                                "awayTeam": away,
                                "score": {"fullTime": {"homeTeam": h, "awayTeam": g}},
                            })

        browser.close()

        if not matches:
            raise RuntimeError("Unable to extract matches from native-stats page")

        return teams, matches


def main():
    api_key = os.getenv("f259f5faf95d420e9df7388e91d487c6")
    try:
        teams, matches = get_teams_and_matches(api_key)
    except requests.HTTPError as e:
        # Try scraping fallback on 403 (forbidden)
        status = None
        try:
            status = e.response.status_code  # type: ignore
        except Exception:
            status = None
        if status == 403:
            try:
                teams, matches = scrape_native_stats(1783)
            except Exception as ex:
                print("Fallback scraping falhou:", ex, file=sys.stderr)
                sys.exit(1)
        else:
            print("Erro ao acessar a API:", e, file=sys.stderr)
            sys.exit(1)

    if not teams:
        print("Nenhum time encontrado.")
        sys.exit(1)

    # Use Flamengo team ID directly (1783) instead of searching by name
    tid = 1783
    last = last_n_matches_for_team(tid, matches, 5)
    if not last:
        print("  (nenhum jogo encontrado)")
        return
    for m in last:
        print("  ", format_match_for_team(m, tid))


if __name__ == "__main__":
    main()
