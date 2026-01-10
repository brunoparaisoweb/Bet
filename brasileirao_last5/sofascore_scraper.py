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
            // Busca todos os títulos de campeonato e seus jogos subsequentes
            const container = document.querySelector('[data-testid="team-matches"]') || document.body;
            const nodes = Array.from(container.querySelectorAll('*'));
            const out = [];
            let i = 0;
            while (i < nodes.length) {
                const node = nodes[i];
                // Procura bloco de campeonato
                if (/brasileir[ãa]o betano/i.test(node.innerText || '')) {
                    // Coleta todos os jogos até o próximo título de campeonato
                    let j = i + 1;
                    while (j < nodes.length) {
                        const n = nodes[j];
                        // Se encontrar outro campeonato, para
                        if (/carioca|libertadores|sul-americana|intercontinental|fifa|amistoso|pyramids|psg|campeonato/i.test(n.innerText || '')) break;
                        // Jogo: link para /match/ e menciona Flamengo
                        if (n.tagName === 'A' && /\/match\//.test(n.getAttribute('href') || '') && /flamengo/i.test(n.innerText || '')) {
                            // Sobe até o pai tr/div mais próximo
                            let parent = n;
                            for (let up = 0; up < 4 && parent; up++) {
                                if (parent.tagName === 'TR' || parent.tagName === 'DIV') break;
                                parent = parent.parentElement;
                            }
                            let bloco = parent ? parent.innerText : n.innerText;
                            bloco = (bloco || '').trim();
                            // Extrai data, placar e times do bloco
                            const dateMatch = bloco.match(/\d{4}-\d{2}-\d{2}/) || bloco.match(/\d{2}\/\d{2}\/\d{4}/);
                            const scoreMatch = bloco.match(/(\d+)\s*[x:–\-]\s*(\d+)/i);
                            out.push({text: bloco, comp: 'Brasileirão Betano', date: dateMatch ? dateMatch[0] : null, score: scoreMatch ? [scoreMatch[1], scoreMatch[2]] : null});
                        }
                        j++;
                    }
                    i = j;
                    continue;
                }
                i++;
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
        txt = item.get("text")
        # Se comp não mencionar Brasileirão Betano, mas também não mencionar outros campeonatos, aceita se adversário for Série A
        comp_ok = False
        if re.search(r"brasileir[ãa]o betano", comp, re.I):
            comp_ok = True
        elif not comp.strip():
            # Se comp está vazio, tenta garantir que não é outro campeonato pelo texto
            if not re.search(r"carioca|libertadores|sul-americana|intercontinental|fifa|amistoso|pyramids|psg", (txt or ""), re.I):
                comp_ok = True
        if not comp_ok:
            if debug:
                print(f"Ignorado: {item.get('text')[:40]}... | comp='{comp}'")
            continue
        if debug:
            print(f"Aceito: {item.get('text')[:40]}... | comp='{comp}'")
        txt = item.get("text")
        if not isinstance(txt, str):
            txt = ""
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        # Data: pega a primeira linha que parece data (dd/mm/aa ou dd/mm/aaaa)
        date = None
        for l in lines:
            m = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4})", l)
            if m:
                date = m.group(1)
                break
        # Times: pega as duas primeiras linhas que não são data, tempo, placar ou resultado
        team_lines = []
        for l in lines:
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
        if len(team_lines) >= 2:
            left = team_lines[0]
            right = team_lines[1]
        else:
            left = right = "-"
        # Placar: busca dois primeiros números "soltos" após os nomes dos times
        nums = []
        found_teams = 0
        for l in lines:
            if found_teams < 2:
                if l == left or l == right:
                    found_teams += 1
                continue
            if re.match(r"^\d+$", l):
                nums.append(int(l))
            if len(nums) >= 2:
                break
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
        # Lista dos clubes da Série A (2024, pode ser atualizada)
        serie_a = [
            "flamengo", "palmeiras", "são paulo", "corinthians", "santos", "vasco da gama", "vasco",
            "mirassol", "vitória", "vitoria", "fortaleza",
            "botafogo", "fluminense", "grêmio", "internacional", "athletico-pr", "atletico-pr", "atlético-pr",
            "atletico-mg", "atlético-mg", "cruzeiro", "bahia", "fortaleza", "cuiabá", "juventude", "bragantino",
            "américa-mg", "goiás", "coritiba", "avaí", "chapecoense", "ceará", "sport", "ponte preta",
            "rb bragantino", "red bull bragantino"
        ]
        # Só adiciona se mandante, visitante e placar forem válidos e adversário for Série A (contém)
        adversario = home["name"].lower() if home["name"].lower() != "flamengo" else away["name"].lower()
        def is_serie_a(nome):
            return any(clube in nome for clube in serie_a)
        if (
            home.get("name", "-") != "-" and
            away.get("name", "-") != "-" and
            home_goals is not None and
            away_goals is not None and
            is_serie_a(adversario)
        ):
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