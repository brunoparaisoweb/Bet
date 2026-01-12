#!/usr/bin/env python3
"""
Scraper para SofaScore - Premier League
Busca últimos 5 jogos de um time específico no campeonato Premier League 2025/2026
"""
from playwright.sync_api import sync_playwright
import time
import re

# IDs dos times da Premier League no SofaScore
PREMIER_LEAGUE_TEAM_IDS = {
    "Arsenal": 42,
    "Manchester City": 17,
    "Man City": 17,
    "Aston Villa": 40,
    "Liverpool": 44,
    "Brentford": 50,
    "Newcastle": 39,
    "Manchester United": 35,
    "Man Utd": 35,
    "Chelsea": 38,
    "Fulham": 43,
    "Sunderland": 41,
    "Brighton": 30,
    "Brighton & Hove Albion": 30,
    "Everton": 48,
    "Crystal Palace": 7,
    "Tottenham": 33,
    "Bournemouth": 60,
    "Leeds United": 34,
    "Leeds": 34,
    "Nottingham Forest": 14,
    "Forest": 14,
    "West Ham": 37,
    "Burnley": 6,
    "Wolverhampton": 3,
    "Wolves": 3
}

def scrape_sofascore_last5(team_id, team_name, debug=False, click_navigation=True):
    """
    Busca os últimos 5 jogos do time no campeonato Premier League 2025/2026.
    
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
                with open("sofascore_pl_debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print("Debug: saved page HTML to sofascore_pl_debug.html")
            
            # Busca todos os cards de competições (cada competição tem seus jogos)
            competition_cards = page.query_selector_all('.card-component')
            
            if debug:
                print(f"Debug: found {len(competition_cards)} competition cards")
            
            jogos_premier = []
            
            # Processa cada card de competição
            for card_idx, card in enumerate(competition_cards):
                try:
                    # Verifica se é o card da Premier League
                    card_html = card.inner_html()
                    
                    # Procura pela imagem do torneio Premier League (ID 17)
                    is_premier_league = 'unique-tournament/17/image' in card_html
                    is_efl_cup = 'unique-tournament/21/image' in card_html
                    is_fa_cup = 'unique-tournament/19/image' in card_html
                    
                    if debug and card_idx < 10:
                        card_text = card.inner_text()
                        first_line = card_text.split('\n')[0] if card_text else ""
                        print(f"Card {card_idx}: Premier={is_premier_league}, EFL={is_efl_cup}, FA={is_fa_cup}, first_line={repr(first_line[:50])}")
                    
                    # Ignora FA Cup e EFL Cup - processa apenas Premier League
                    if is_fa_cup or is_efl_cup:
                        if debug:
                            print(f"Debug: Skipping card {card_idx} (FA Cup or EFL Cup)")
                        continue
                    
                    # Se não for Premier League, pula
                    if not is_premier_league:
                        continue
                    
                    if debug:
                        print(f"Debug: Processing Premier League card {card_idx}")
                    
                    # Busca eventos dentro deste card da Premier League
                    eventos = card.query_selector_all('[class*="event"]')
                    
                    if debug:
                        print(f"Debug: found {len(eventos)} events in Premier League card")
                    
                    # Processa cada evento
                    for i, evento in enumerate(eventos):
                        try:
                            # Pega o texto completo do evento com tratamento de erro
                            try:
                                texto = evento.inner_text()
                            except Exception:
                                # Se inner_text falhar, tenta text_content
                                try:
                                    texto = evento.text_content()
                                except Exception:
                                    # Se ambos falharem, pula este evento
                                    continue
                            
                            if not texto:
                                continue
                            
                            # Debug: mostra eventos
                            if debug:
                                linhas = texto.strip().split('\n')
                                date = linhas[0] if len(linhas) > 0 else ""
                                if i < 15 or ("F2" in texto or "Finalizado" in texto):
                                    print(f"  Event {i}: text={repr(texto[:200])}")
                            
                            # Verifica se é jogo finalizado (F2°T ou apenas F seguido de números)
                            is_finished = ("F2°T" in texto or "F2°" in texto or "F2T" in texto or
                                         "Finalizado" in texto or 
                                         (re.search(r'\nF\n', texto) and re.search(r'\d+', texto)))
                            
                            if debug and is_finished:
                                print(f"    [FINISHED] Detected finished match: {repr(texto[:100])}")
                            
                            if is_finished:
                                linhas = texto.strip().split('\n')
                                
                                # Extrai informações
                                comp = "Premier League"
                                date = None
                                home = None
                                away = None
                                home_score = None
                                away_score = None
                                
                                # Parse das linhas
                                for idx, linha in enumerate(linhas):
                                    linha_clean = linha.strip()
                                    
                                    if re.match(r'\d{2}/\d{2}/\d{2}', linha_clean):
                                        date = linha_clean
                                    elif linha_clean and len(linha_clean) > 2:
                                        # Ignora marcadores de status (F2°T, W, D, L, etc) e números isolados
                                        if re.match(r'^F\d', linha_clean):  # F2°T, F2T, etc
                                            continue
                                        if re.match(r'^[FDWLE]$', linha_clean):  # W, D, L, E sozinhos
                                            continue
                                        if re.match(r'^\d+$', linha_clean):  # Números isolados
                                            continue
                                        if re.match(r'^\d{2}:\d{2}$', linha_clean):  # Horários (14:30)
                                            continue
                                        
                                        # Possível nome de time
                                        if not home:
                                            home = linha_clean
                                        elif not away and linha_clean != home:
                                            away = linha_clean
                                
                                # Extrai placares (procura por números isolados)
                                scores = re.findall(r'\n(\d+)\n', texto)
                                if len(scores) >= 2:
                                    try:
                                        home_score = int(scores[0])
                                        away_score = int(scores[1])
                                    except:
                                        pass
                                
                                # Se encontrou todas as informações, adiciona o jogo
                                if home and away and home_score is not None and away_score is not None:
                                    if debug:
                                        print(f"  [OK] Jogo valido: {home} {home_score} x {away_score} {away}")
                                    
                                    jogos_premier.append({
                                        "competition": {"name": "Premier League"},
                                        "startDate": date or "",
                                        "homeTeam": {"name": home},
                                        "awayTeam": {"name": away},
                                        "score": {
                                            "fullTime": {
                                                "homeTeam": home_score,
                                                "awayTeam": away_score
                                            }
                                        }
                                    })
                                else:
                                    if debug:
                                        print(f"    [SKIP] Missing data - home={repr(home)}, away={repr(away)}, hs={home_score}, as={away_score}")
                        
                        except Exception as e:
                            if debug:
                                print(f"Debug: Erro ao processar evento {i}: {e}")
                            continue
                
                except Exception as e:
                    if debug:
                        print(f"Debug: Erro ao processar card {card_idx}: {e}")
                    continue
            
            # Retorna até 5 jogos mais recentes
            jogos = jogos_premier[:5]
            
        except Exception as e:
            print(f"Erro ao buscar jogos: {e}")
        
        finally:
            browser.close()
    
    return jogos

if __name__ == "__main__":
    # Teste com alguns times
    times_teste = [
        ("Manchester City", 17),
        ("Arsenal", 42),
        ("Liverpool", 44)
    ]
    
    for nome, team_id in times_teste:
        print(f"\n=== Testando {nome} (ID: {team_id}) ===")
        jogos = scrape_sofascore_last5(team_id, nome, debug=True)
        print(f"Encontrados {len(jogos)} jogos da Premier League")
        for jogo in jogos:
            home = jogo.get("homeTeam", {}).get("name", "?")
            away = jogo.get("awayTeam", {}).get("name", "?")
            score = jogo.get("score", {}).get("fullTime", {})
            hs = score.get("homeTeam", "?")
            aws = score.get("awayTeam", "?")
            print(f"  {home} {hs} x {aws} {away}")
