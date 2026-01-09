#!/usr/bin/env python3
"""Scrape SofaScore Flamengo page to get last 5 matches in Brasileirão (Betano).

Requires Playwright: `pip install playwright` and `playwright install chromium`.
Usage:
    python sofascore_scraper.py
"""
from __future__ import annotations
import re
import sys
from typing import List, Dict

try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print("Playwright is required. Install with: pip install playwright", file=sys.stderr)
    raise

URL = "https://www.sofascore.com/pt/football/team/flamengo/5981"

def scrape_sofascore_last5(debug: bool = False) -> List[Dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1200)
        js = r"""
        (() => {
            const nodes = Array.from(document.querySelectorAll('a[href*="/match/"]'));
            const out = [];
            for (const node of nodes) {
                const text = (node.innerText || node.textContent || '').trim();
                if (!text) continue;
                if (!/flamengo/i.test(text)) continue;
                let comp = '';
                let el = node;
                for (let depth = 0; depth < 8 && el; depth++) {
                    const prev = el.previousElementSibling;
                    if (prev && /brasileir|betano/i.test(prev.innerText || '')) { comp = prev.innerText.trim(); break; }
                    const parentPrev = el.parentElement ? el.parentElement.previousElementSibling : null;
                    if (parentPrev && /brasileir|betano/i.test(parentPrev.innerText || '')) { comp = parentPrev.innerText.trim(); break; }
                    el = el.parentElement;
                }
                const dateMatch = text.match(/\d{4}-\d{2}-\d{2}/) || text.match(/\d{2}\/\d{2}\/\d{4}/);
                const scoreMatch = text.match(/(\d+)\s*[x:–\-]\s*(\d+)/i);
                out.push({text, comp, date: dateMatch ? dateMatch[0] : null, score: scoreMatch ? [scoreMatch[1], scoreMatch[2]] : null});
            }
            return out;
        })();
        """
        candidates = []
        page_html = None
        try:
            candidates = page.evaluate(js)
            page_html = page.content()
        except Exception:
            text = page.inner_text("body")
            page_html = text
        browser.close()
    print(f"Debug: found {len(candidates)} candidate nodes")
    for i, c in enumerate(candidates[:10]):
        print(i, c)
    try:
        with open("sofascore_debug.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        print("Debug: saved page HTML to sofascore_debug.html")
    except Exception as e:
        print("Debug: failed saving HTML:", e)
    results: List[Dict] = []
    for item in candidates:
        comp = (item.get("comp") or "")
        # Filtro: só aceita se comp for exatamente "Brasileirão Betano" (ignorando maiúsculas/minúsculas e espaços)
        # Aceita só se "Brasileirão Betano" for uma linha isolada no campo comp
        comp_lines = [line.strip().lower() for line in comp.splitlines()]
        if "brasileirão betano" not in comp_lines:
            if debug:
                print(f"Ignorado: {item.get('text')[:40]}... | comp='{comp}'")
            continue
        if debug:
            print(f"Aceito: {item.get('text')[:40]}... | comp='{comp}'")
        txt = item.get("text")
        if not isinstance(txt, str):
            txt = ""
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        date = item.get("date")
        if not date:
            # Busca a primeira linha que parece uma data
            for l in lines:
                m = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4})", l)
                if m:
                    date = m.group(1)
                    break
        # Busca a primeira linha que parece uma data, se necessário
        date = item.get("date")
        if not date:
            for l in lines:
                m = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4})", l)
                if m:
                    date = m.group(1)
                    break
        # Procura linhas que parecem nomes de times (ignorando datas, tempos, placares)
        team_lines = []
        score = item.get("score")
        for l in lines:
            # Considera nome de time se não for data, tempo, placar ou resultado
            if re.match(r"\d{1,2}/\d{1,2}/\d{2,4}", l):
                continue
            if re.match(r"[FA][P\d]+", l):  # F2°T, AP, etc
                continue
            if re.match(r"\d+$", l):
                continue
            if re.match(r"[VDE]$", l, re.I):
                continue
            if re.match(r"\d+\s*[x:–\-]\s*\d+", l):
                continue
            team_lines.append(l)
        # Espera-se que os dois primeiros nomes de time sejam mandante e visitante
        if len(team_lines) >= 2:
            left = team_lines[0]
            right = team_lines[1]
        else:
            left = right = "-"
        # Placar: tenta extrair do campo score, se não conseguir, tenta pegar dois primeiros números das linhas
        if score:
            try:
                home_goals = int(score[0])
                away_goals = int(score[1])
            except Exception:
                home_goals = away_goals = None
        else:
            # Busca dois primeiros números "soltos" nas linhas
            nums = []
            for l in lines:
                if re.match(r"^\d+$", l):
                    nums.append(int(l))
            if len(nums) >= 2:
                home_goals, away_goals = nums[0], nums[1]
            else:
                home_goals = away_goals = None
        # Identifica quem é Flamengo
        if re.search(r"^flamengo\\b", left, re.I) or ("flamengo" in left.lower() and "flamengo" in left.lower().split()[0:2]):
            home = {"id": 5981, "name": "Flamengo"}
            away = {"id": None, "name": right}
        elif "flamengo" in right.lower():
            away = {"id": 5981, "name": "Flamengo"}
            home = {"id": None, "name": left}
        else:
            home = {"id": 5981, "name": left}
            away = {"id": None, "name": right}
        results.append({
            "utcDate": date,
            "homeTeam": home,
            "awayTeam": away,
            "score": {"fullTime": {"homeTeam": home_goals, "awayTeam": away_goals}},
        })
    # Ordena por data (se possível) do mais recente para o mais antigo
    def parse_date(d):
        if not d:
            return "0000-00-00"
        if re.match(r"\d{2}/\d{2}/\d{2,4}", d):
            parts = d.split("/")
            if len(parts[2]) == 2:
                parts[2] = "20" + parts[2]
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return d
    results.sort(key=lambda x: parse_date(x["utcDate"]), reverse=True)
    return results[:5]

def main():
    matches = scrape_sofascore_last5(debug=True)
    if not matches:
        print("Nenhum jogo encontrado.")
        return
    for m in matches:
        utc = m.get("utcDate") or ""
        home = m.get("homeTeam", {}).get("name")
        away = m.get("awayTeam", {}).get("name")
        full = m.get("score", {}).get("fullTime", {})
        hg = full.get("homeTeam")
        ag = full.get("awayTeam")
        score_text = f"{hg} x {ag}" if hg is not None and ag is not None else "-"
        print(f"{utc} | {home} vs {away} | {score_text}")

if __name__ == "__main__":
    main()