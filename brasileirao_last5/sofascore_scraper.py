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

def scrape_sofascore_last5(team_id: int = 5981, team_name: str = "flamengo", debug: bool = False) -> List[Dict]:
    url = f"https://www.sofascore.com/pt/football/team/{team_name.lower()}/{team_id}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)  # Aguarda carregamento inicial
        
        # Clica no logo/imagem do time para carregar as informações
        try:
            # Procura pela imagem do time
            img_selector = f"img[alt*='{team_name}'], img[src*='team/{team_id}/image']"
            img = page.query_selector(img_selector)
            if img:
                img.click()
                page.wait_for_timeout(2000)
                if debug:
                    print(f"Debug: Clicou no logo do time")
        except Exception as e:
            if debug:
                print(f"Debug: Não conseguiu clicar no logo: {e}")
        
        # Scroll para baixo para forçar carregamento de conteúdo
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        
        # Clica em todas as abas possíveis ('Todos', 'Fora', 'Away', etc.)
        abas = ["Todos", "Fora", "Away", "All", "Todos os jogos"]
        all_candidates = []
        js = r"""
(() => {
    // Busca TODOS os elementos que contêm "Brasileirão Betano" e seus jogos adjacentes
    const allElements = Array.from(document.querySelectorAll('*'));
    const out = [];
    
    for (let i = 0; i < allElements.length; i++) {
        const el = allElements[i];
        const text = (el.innerText || '').trim();
        
        // Se encontrar "Brasileirão Betano"
        if (/brasileir[ãa]o betano/i.test(text) && text.length < 100) {
            // Procura jogos nos próximos elementos
            for (let j = i + 1; j < Math.min(i + 50, allElements.length); j++) {
                const candidate = allElements[j];
                const cText = (candidate.innerText || '').trim();
                
                // Para se encontrar outro campeonato
                if (/carioca|libertadores|sul-americana|intercontinental|fifa/i.test(cText) && cText.length < 50) break;
                
                // Se parecer um bloco de jogo (tem data + time + números)
                if (/\d{2}\/\d{2}\/\d{2}/.test(cText) && cText.length > 20 && cText.length < 300) {
                    const dateMatch = cText.match(/(\d{2}\/\d{2}\/\d{2,4})/);
                    const scoreMatch = cText.match(/(\d+)\s*[x:–\-]\s*(\d+)/i);
                    out.push({text: cText, comp: 'Brasileirão Betano', date: dateMatch ? dateMatch[0] : null, score: scoreMatch ? [scoreMatch[1], scoreMatch[2]] : null});
                }
            }
        }
    }
    
    return out;
})();
        """
        
        # PRIMEIRO: Coleta jogos da página inicial (mais recentes)
        for aba in abas:
            try:
                btn = page.query_selector(f"button:has-text('{aba}')")
                if btn:
                    btn.click()
                    page.wait_for_timeout(1500)
            except Exception:
                continue
            try:
                candidates = page.evaluate(js)
                all_candidates.extend(candidates)
            except Exception:
                continue
        
        # DEPOIS: Clica na seta esquerda para carregar jogos mais antigos
        try:
            clicked = page.evaluate("""
                (() => {
                    // Procura pelo botão específico com SVG de seta esquerda
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        // Verifica se contém SVG com viewBox="0 0 24 24" e path com d começando com "M6 11.99"
                        const svg = btn.querySelector('svg[viewBox="0 0 24 24"]');
                        if (svg) {
                            const path = svg.querySelector('path');
                            if (path && path.getAttribute('d').startsWith('M6 11.99')) {
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                })();
            """)
            if clicked:
                page.wait_for_timeout(3000)  # Aguarda carregar novos jogos
        except Exception:
            pass
        
        # Coleta jogos da página após clicar na seta (jogos mais antigos)
        for aba in abas:
            try:
                btn = page.query_selector(f"button:has-text('{aba}')")
                if btn:
                    btn.click()
                    page.wait_for_timeout(1500)
            except Exception:
                continue
            try:
                candidates = page.evaluate(js)
                all_candidates.extend(candidates)
            except Exception:
                continue
        # Remove duplicados pelo texto do bloco
        seen = set()
        unique_candidates = []
        for c in all_candidates:
            t = c.get('text')
            if t and t not in seen:
                unique_candidates.append(c)
                seen.add(t)
        candidates = unique_candidates
        page_html = None
        try:
            page_html = page.content()
        except Exception:
            text = page.inner_text("body")
            page_html = text
        browser.close()
    print(f"Debug: found {len(candidates)} candidate nodes")
    if debug:
        print(f"Debug: URL acessada: {url}")
        # Mostra amostra do conteúdo da página
        if page_html and isinstance(page_html, str):
            # Procura por "Brasileirão" no HTML
            brasileirao_count = page_html.lower().count("brasileirão")
            betano_count = page_html.lower().count("betano")
            print(f"Debug: 'Brasileirão' aparece {brasileirao_count} vezes no HTML")
            print(f"Debug: 'Betano' aparece {betano_count} vezes no HTML")
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
        
        # Filtra apenas jogos de 2025
        if date:
            parts = date.split("/")
            year = parts[2] if len(parts) == 3 else None
            if year:
                if len(year) == 2:
                    year = "20" + year
                if year != "2025":
                    if debug:
                        print(f"Descartado: jogo de {year} (queremos apenas 2025)")
                    continue
        
        # Times: pega todas as linhas que não são data, tempo, placar ou resultado
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
        # Procura o time em qualquer linha de time
        target_idx = None
        for idx, t in enumerate(team_lines):
            if team_name.lower() in t.lower():
                target_idx = idx
                break
        if target_idx is not None and len(team_lines) >= 2:
            other_idx = 1 - target_idx if len(team_lines) == 2 else (target_idx + 1 if target_idx == 0 else target_idx - 1)
            left = team_lines[0]
            right = team_lines[1] if len(team_lines) > 1 else "-"
            if target_idx == 0:
                home = {"id": team_id, "name": team_lines[0]}
                away = {"id": None, "name": team_lines[1] if len(team_lines) > 1 else "-"}
                adversario_nome = team_lines[1] if len(team_lines) > 1 else "-"
            else:
                home = {"id": None, "name": team_lines[0]}
                away = {"id": team_id, "name": team_lines[1] if len(team_lines) > 1 else "-"}
                adversario_nome = team_lines[0]
        else:
            if debug:
                print(f"Descartado: não reconheceu {team_name} em {team_lines}")
            continue
        # Placar: busca números "soltos" após os nomes dos times (1º e 3º número)
        nums = []
        found_teams = 0
        for l in lines:
            if found_teams < 2:
                if l in team_lines:
                    found_teams += 1
                continue
            if re.match(r"^\d+$", l):
                nums.append(int(l))
            if len(nums) >= 4:
                break
        if len(nums) >= 4:
            home_goals, away_goals = nums[0], nums[2]
        elif len(nums) >= 2:
            home_goals, away_goals = nums[0], nums[1]
        else:
            home_goals = away_goals = None
        # Lista dos clubes da Série A (2024, pode ser atualizada)
        serie_a = [
            "flamengo", "palmeiras", "são paulo", "corinthians", "santos", "vasco da gama", "vasco",
            "mirassol", "vitória", "vitoria", "fortaleza",
            "botafogo", "fluminense", "grêmio", "internacional", "athletico-pr", "atletico-pr", "atlético-pr",
            "atletico-mg", "atlético-mg", "cruzeiro", "bahia", "fortaleza", "cuiabá", "juventude", "bragantino",
            "américa-mg", "goiás", "coritiba", "avaí", "chapecoense", "ceará", "sport", "ponte preta",
            "rb bragantino", "red bull bragantino"
        ]
        import unicodedata
        def normalize_nome(nome):
            nome = nome.lower()
            nome = unicodedata.normalize('NFKD', nome)
            nome = ''.join([c for c in nome if not unicodedata.combining(c)])
            nome = nome.replace('-', '').replace(' ', '')
            return nome
        serie_a_norm = [normalize_nome(clube) for clube in serie_a]
        def is_serie_a(nome):
            nome_norm = normalize_nome(nome)
            return any(clube in nome_norm for clube in serie_a_norm)
        if (
            home.get("name", "-") != "-" and
            away.get("name", "-") != "-" and
            home_goals is not None and
            away_goals is not None and
            is_serie_a(adversario_nome)
        ):
            results.append({
                "utcDate": date,
                "homeTeam": home,
                "awayTeam": away,
                "score": {"fullTime": {"homeTeam": home_goals, "awayTeam": away_goals}},
            })
        elif debug:
            print(f"Descartado: {home['name']} x {away['name']} | adversario norm: {normalize_nome(adversario_nome)}")
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
    matches = scrape_sofascore_last5(team_id=5981, team_name="flamengo", debug=True)
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