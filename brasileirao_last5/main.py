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

COMP = "BSA"  # competition code for Campeonato Brasileiro Série A (football-data.org)


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


def main():
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    try:
        teams, matches = get_teams_and_matches(api_key)
    except requests.HTTPError as e:
        print("Erro ao acessar a API:", e, file=sys.stderr)
        sys.exit(1)

    if not teams:
        print("Nenhum time encontrado.")
        sys.exit(1)

    for t in teams:
        tid = t.get("id")
        tname = t.get("name") or t.get("shortName") or t.get("clubName") or "Unknown"
        print(f"\n=== {tname} ===")
        last = last_n_matches_for_team(tid, matches, 5)
        if not last:
            print("  (nenhum jogo encontrado)")
            continue
        for m in last:
            print("  ", format_match_for_team(m, tid))


if __name__ == "__main__":
    main()
