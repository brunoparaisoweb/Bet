#!/usr/bin/env python3
"""
Scraper para SofaScore - LaLiga
Busca últimos 5 jogos de um time específico no campeonato LaLiga 2025/2026
"""
from playwright.sync_api import sync_playwright
import time
import re

# IDs dos times da LaLiga no SofaScore
LALIGA_TEAM_IDS = {
    "Barcelona": 2817,
    "Real Madrid": 2829,
    "Villarreal": 2819,
    "Atlético Madrid": 2836,
    "Atl. Madrid": 2836,
    "Atlético de Madrid": 2836,
    "Espanyol": 2814,
    "Real Betis": 2816,
    "Betis": 2816,
    "Celta": 2821,
    "Celta de Vigo": 2821,
    "Athletic Club": 2825,
    "Athletic Bilbao": 2825,
    "Elche": 2846,
    "Rayo Vallecano": 2818,
    "Real Sociedad": 2824,
    "Getafe": 2859,
    "Girona": 24264,
    "Sevilla": 2833,
    "Osasuna": 2820,
    "Alavés": 2885,
    "Mallorca": 2826,
    "Valencia": 2828,
    "Levante": 2849,
    "Real Oviedo": 2851
}

def scrape_sofascore_last5(team_id, team_name, debug=False, click_navigation=True):
    """
    Busca os últimos 5 jogos do time no campeonato LaLiga 2025/2026.
    Navega dentro do card "Matches" para encontrar jogos mais antigos se necessário.
    
    Args:
        team_id: ID do time no SofaScore
        team_name: Nome do time (para debug)
        debug: Se True, salva HTML da página para debug
        click_navigation: Se True, clica no link de navegação antes de buscar
    """
    jogos = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # URL do time no SofaScore
            url = f"https://www.sofascore.com/pt/time/futebol/{team_name.lower().replace(' ', '-')}/{team_id}"
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            # Scroll para carregar conteúdo dinâmico
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            
            # Salva HTML para debug se solicitado
            if debug:
                with open("sofascore_laliga_debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print("Debug: saved page HTML to sofascore_laliga_debug.html")
            
            jogos_laliga = []
            jogos_ids = set()  # Para evitar duplicatas
            max_cliques = 15
            cliques_realizados = 0
            
            while len(jogos_laliga) < 5 and cliques_realizados < max_cliques:
                # Busca todos os cards
                competition_cards = page.query_selector_all('.card-component')
                
                if debug:
                    print(f"Debug: Tentativa {cliques_realizados + 1} - {len(jogos_laliga)} jogos coletados")
                
                # Encontra o card "Matches" (que contém todos os jogos)
                matches_card = None
                matches_text = ""
                for card in competition_cards:
                    try:
                        card_text = card.inner_text()
                        first_line = card_text.split('\n')[0] if card_text else ""
                        if first_line in ['Matches', 'Partidas']:
                            matches_card = card
                            matches_text = card_text
                            break
                    except:
                        continue
                
                if not matches_card:
                    if debug:
                        print(f"Debug: Card de Matches não encontrado")
                    break
                
                # Processa o texto do card Matches para extrair jogos LaLiga
                lines = matches_text.split('\n')
                current_competition = None
                i = 0
                
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Detecta headers de campeonato (SEMPRE atualiza o campeonato atual)
                    if line in ['LaLiga', 'Copa del Rey', 'UEFA Champions League', 'UEFA Europa League', 
                               'UEFA Europa Conference League', 'Liga dos Campeões da UEFA', 'UEFA Liga Europa',
                               'Liga Europa da UEFA', 'Supercopa de España', 'Supercopa de Espa±a', 'Supercopa']:
                        current_competition = line
                        if debug:
                            print(f"  >> Campeonato: {current_competition}")
                        i += 1
                        continue
                    
                    # Se estamos em LaLiga e é uma data de jogo
                    if current_competition == 'LaLiga' and re.match(r'\d{2}/\d{2}/\d{2}', line):
                        date = line
                        i += 1
                        if i >= len(lines):
                            break
                            
                        status_line = lines[i].strip()
                        
                        # Se for FT ou F2°T (jogo finalizado)
                        if status_line == 'FT' or 'F2' in status_line:
                            i += 1
                            if i >= len(lines):
                                break
                            
                            # Próximas linhas: home, away, scores
                            home = lines[i].strip() if i < len(lines) else None
                            i += 1
                            away = lines[i].strip() if i < len(lines) else None
                            i += 1
                            
                            # Coletar placares (formato: score_home, ??, score_away, ??)
                            scores = []
                            while i < len(lines) and len(scores) < 4:
                                score_line = lines[i].strip()
                                if re.match(r'^\d+$', score_line):
                                    scores.append(int(score_line))
                                    i += 1
                                elif score_line in ['W', 'D', 'L']:
                                    i += 1
                                    break
                                else:
                                    break
                            
                            # Formato: score_home, ??, score_away, ?? 
                            home_score = scores[0] if len(scores) >= 1 else None
                            away_score = scores[2] if len(scores) >= 3 else (scores[1] if len(scores) >= 2 else None)
                            
                            if home and away and home_score is not None and away_score is not None:
                                # Cria ID único para evitar duplicatas
                                jogo_id = f"{home}{away}{home_score}{away_score}{date}"
                                
                                if jogo_id not in jogos_ids:
                                    jogos_ids.add(jogo_id)
                                    if debug:
                                        print(f"  [OK] LaLiga: {home} {home_score} x {away_score} {away} ({date})")
                                    jogos_laliga.append({
                                        "competition": {"name": "LaLiga"},
                                        "startDate": date,
                                        "homeTeam": {"name": home},
                                        "awayTeam": {"name": away},
                                        "score": {
                                            "fullTime": {
                                                "homeTeam": home_score,
                                                "awayTeam": away_score
                                            }
                                        }
                                    })
                            continue
                    i += 1
                
                # Se já temos 5 jogos, termina
                if len(jogos_laliga) >= 5:
                    if debug:
                        print(f"Debug: Coletados {len(jogos_laliga)} jogos LaLiga, encerrando")
                    break
                
                # Navegar para jogos anteriores clicando na seta esquerda DENTRO do card Matches
                cliques_realizados += 1
                
                try:
                    nav_buttons = matches_card.query_selector_all('button')
                    if nav_buttons and len(nav_buttons) > 0:
                        left_button = nav_buttons[0]  # Primeiro botão é seta esquerda
                        
                        if left_button.is_visible() and not left_button.get_attribute('disabled'):
                            if debug:
                                print(f"Debug: Clicando na seta esquerda dentro do card Matches...")
                            left_button.click()
                            page.wait_for_timeout(2000)
                        else:
                            if debug:
                                print(f"Debug: Botão de navegação desabilitado ou não visível")
                            break
                    else:
                        if debug:
                            print(f"Debug: Botões de navegação não encontrados no card")
                        break
                except Exception as e:
                    if debug:
                        print(f"Debug: Erro ao navegar: {e}")
                    break
            
            # Retorna os 5 jogos mais recentes da LaLiga
            jogos = jogos_laliga[:5]
            
            if debug:
                print(f"Debug: Retornando {len(jogos)} jogos LaLiga")
            
        except Exception as e:
            print(f"Erro ao buscar jogos: {e}")
        
        finally:
            browser.close()
    
    return jogos

if __name__ == "__main__":
    # Teste com alguns times
    times_teste = [
        ("Barcelona", 2817),
        ("Real Madrid", 2829),
        ("Atlético Madrid", 2836)
    ]
    
    for nome, team_id in times_teste:
        print(f"\n=== Testando {nome} (ID: {team_id}) ===")
        jogos = scrape_sofascore_last5(team_id, nome, debug=True)
        print(f"Encontrados {len(jogos)} jogos da LaLiga")
        for jogo in jogos:
            home = jogo.get("homeTeam", {}).get("name", "?")
            away = jogo.get("awayTeam", {}).get("name", "?")
            score = jogo.get("score", {}).get("fullTime", {})
            hs = score.get("homeTeam", "?")
            aws = score.get("awayTeam", "?")
            print(f"  {home} {hs} x {aws} {away}")
