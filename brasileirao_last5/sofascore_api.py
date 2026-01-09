#!/usr/bin/env python3
"""Query SofaScore public API for Flamengo last 5 matches in Brasileirão 2025.

This script tries several SofaScore endpoints (best-effort). If the first
endpoint doesn't work, it will try alternates. The JSON structure returned
by SofaScore can vary; parsing attempts to be resilient.

Usage:
    python sofascore_api.py
"""
from __future__ import annotations
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

import requests

TEAM_ID = 5981  # SofaScore ID for Flamengo
SEASON_YEAR = 2025
COMPETITION_KEYWORDS = ("brasileir", "betano")


def try_urls(team_id: int) -> List[str]:
    # common SofaScore API URL patterns to try
    return [
        f"https://api.sofascore.com/api/team/{team_id}/events",
        f"https://api.sofascore.com/api/team/{team_id}/events/season/{SEASON_YEAR}",
        f"https://api.sofascore.com/api/team/{team_id}/events?page=0",
    ]


def fetch_json(url: str) -> Any:
    headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


def extract_matches_from_events(data: Any) -> List[Dict[str, Any]]:
    events = []
    # SofaScore often wraps events under 'events' or 'items' or is the root list
    if isinstance(data, dict):
        if "events" in data and isinstance(data["events"], list):
            events = data["events"]
        elif "items" in data and isinstance(data["items"], list):
            events = data["items"]
        else:
            # try to find the first list value
            for v in data.values():
                if isinstance(v, list):
                    events = v
                    break
    elif isinstance(data, list):
        events = data

    normalized = []
    for e in events:
        try:
            # try several common fields
            # date: startTimestamp (seconds) or startDate
            date = None
            if isinstance(e.get("startTimestamp"), (int, float)):
                date = datetime.utcfromtimestamp(int(e.get("startTimestamp"))).isoformat()
            elif e.get("startDate"):
                date = e.get("startDate")
            elif e.get("event") and e["event"].get("startTimestamp"):
                date = datetime.utcfromtimestamp(int(e["event"]["startTimestamp"])) .isoformat()

            # competition / tournament name
            comp = None
            if e.get("tournament"):
                comp = e.get("tournament").get("name") if isinstance(e.get("tournament"), dict) else e.get("tournament")
            if not comp and e.get("competition"):
                comp = e.get("competition").get("name") if isinstance(e.get("competition"), dict) else e.get("competition")

            # season year
            season_year = None
            if e.get("season") and isinstance(e.get("season"), dict):
                # possible fields: 'name' or 'startYear'
                sy = e.get("season").get("name") or e.get("season").get("startYear")
                if isinstance(sy, int):
                    season_year = sy
                elif isinstance(sy, str) and sy.isdigit():
                    season_year = int(sy)

            # teams and scores
            home = None
            away = None
            home_goals = None
            away_goals = None

            # direct fields
            if e.get("homeTeam") and e.get("awayTeam"):
                home = e.get("homeTeam")
                away = e.get("awayTeam")
            elif e.get("home") and e.get("away"):
                home = e.get("home")
                away = e.get("away")

            # score fields
            if e.get("score") and isinstance(e.get("score"), dict):
                # try full time
                ft = e.get("score").get("fullTime") or e.get("score").get("ft")
                if ft and isinstance(ft, dict):
                    home_goals = ft.get("home") or ft.get("homeTeam") or ft.get("homeGoals")
                    away_goals = ft.get("away") or ft.get("awayTeam") or ft.get("awayGoals")
                else:
                    # flattened
                    home_goals = e.get("homeScore") or e.get("homeGoals")
                    away_goals = e.get("awayScore") or e.get("awayGoals")

            # determine competition match
            comp_lower = (comp or "").lower()
            if not any(k in comp_lower for k in COMPETITION_KEYWORDS):
                continue
            if season_year and season_year != SEASON_YEAR:
                continue

            # build normalized event
            normalized.append({
                "utcDate": date,
                "competition": comp,
                "homeTeam": {"id": (home or {}).get("id"), "name": (home or {}).get("name")},
                "awayTeam": {"id": (away or {}).get("id"), "name": (away or {}).get("name")},
                "score": {"fullTime": {"homeTeam": home_goals, "awayTeam": away_goals}},
            })
        except Exception:
            continue

    return normalized


def main():
    urls = try_urls(TEAM_ID)
    data = None
    for u in urls:
        try:
            data = fetch_json(u)
            break
        except Exception:
            time.sleep(0.2)
            continue

    if data is None:
        print("Não foi possível obter dados da API do SofaScore.")
        sys.exit(1)

    matches = extract_matches_from_events(data)
    # sort by date descending
    def keyfn(m):
        d = m.get("utcDate")
        try:
            return d or ""
        except Exception:
            return ""

    matches.sort(key=keyfn, reverse=True)
    last5 = matches[:5]

    if not last5:
        print("Nenhum jogo encontrado para Brasileirão 2025 via SofaScore API.")
        sys.exit(0)

    for m in last5:
        date = m.get("utcDate") or ""
        home = m.get("homeTeam", {}).get("name")
        away = m.get("awayTeam", {}).get("name")
        ft = m.get("score", {}).get("fullTime", {})
        hg = ft.get("homeTeam")
        ag = ft.get("awayTeam")
        score_text = f"{hg} x {ag}" if hg is not None and ag is not None else "-"
        print(f"{date} | {home} vs {away} | {score_text}")


if __name__ == "__main__":
    main()
