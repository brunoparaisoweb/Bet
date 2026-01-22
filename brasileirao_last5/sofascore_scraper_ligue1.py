#!/usr/bin/env python3
"""
Scraper para SofaScore - Ligue 1
Busca últimos 5 jogos de um time específico no campeonato Ligue 1 2025/2026
"""
from playwright.sync_api import sync_playwright
import time
import re

# IDs dos times da Ligue 1 no SofaScore
LIGUE1_TEAM_IDS = {
    "Lens": 1648,
    "Paris Saint-Germain": 1644,
    "Olympique de Marselha": 1641,
    "Lyon": 1649,
    "Lille": 1643,
    "Rennes": 1658,
    "Strasbourg": 1659,  # CORRIGIDO: era 1658 (Rennes)
    "Toulouse": 1681,
    "Monaco": 1653,
    "Brest": 1715,
    "Angers": 1684,
    "Lorient": 1656,
    "Paris FC": 6070,
    "Le Havre": 1662,
    "Nice": 1661,
    "Nantes": 1647,
    "Auxerre": 1646,
    "Metz": 1651
}

# Slugs dos times no SofaScore (alguns times têm slugs diferentes do nome)
LIGUE1_SOFASCORE_SLUGS = {
    "Lens": "lens",
    "Paris Saint-Germain": "paris-saint-germain",
    "Olympique de Marselha": "marseille",
    "Lyon": "lyon",
    "Lille": "lille",
    "Rennes": "rennes",
    "Strasbourg": "strasbourg",
    "Toulouse": "toulouse",
    "Monaco": "monaco",
    "Brest": "brest",
    "Angers": "angers",
    "Lorient": "lorient",
    "Paris FC": "paris-fc",
    "Le Havre": "le-havre",
    "Nice": "nice",
    "Nantes": "nantes",
    "Auxerre": "auxerre",
    "Metz": "metz"
}

def scrape_sofascore_last5(team_id, team_name, debug=False, click_navigation=True):
    """
    Busca os últimos 5 jogos do time no campeonato Ligue 1 2025/2026.
    
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
            # URL do time no SofaScore - usar slug correto se disponível
            team_slug = LIGUE1_SOFASCORE_SLUGS.get(team_name, team_name.lower().replace(' ', '-'))
            url = f"https://www.sofascore.com/pt/time/futebol/{team_slug}/{team_id}"
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
                with open(f"sofascore_ligue1_debug_{team_name.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print(f"Debug: saved page HTML to sofascore_ligue1_debug_{team_name.replace(' ', '_')}.html")
            
            # Busca todos os cards de competições (cada competição tem seus jogos)
            competition_cards = page.query_selector_all('.card-component')
            
            if debug:
                print(f"Debug: found {len(competition_cards)} competition cards")
            
            jogos_ligue1 = []
            jogos_vistos = set()  # Para evitar duplicatas (data + times)
            
            # Processa cada card de competição
            for card_idx, card in enumerate(competition_cards):
                try:
                    # Verifica se é o card da Ligue 1
                    card_html = card.inner_html()
                    card_text = card.inner_text()
                    first_line = card_text.split('\n')[0] if card_text else ""
                    
                    # Procura pela imagem do torneio Ligue 1 (ID 34)
                    is_ligue1 = 'unique-tournament/34/image' in card_html
                    is_coupe = 'tournament/53/image' in card_html  # Coupe de France
                    is_trophee = 'tournament/465/image' in card_html  # Trophée des Champions
                    is_champions = 'tournament/7/image' in card_html  # Liga dos Campeões
                    is_destacado = 'Destacado' in first_line  # Card "Destacado" tem formato diferente
                    # Verificação adicional por texto - cobrir todas as variações da Coupe de France
                    is_coupe_text = any(x in card_text.lower() for x in ['coupe de france 2025/26', 'coupe de france 2024/25', 'coupe de france'])
                    
                    if debug and card_idx < 10:
                        print(f"Card {card_idx}: Ligue1={is_ligue1}, Coupe={is_coupe}, Trophée={is_trophee}, Champions={is_champions}, Destacado={is_destacado}, Coupe_text={is_coupe_text}, first_line={repr(first_line[:50])}")
                    
                    # Só processa se for Ligue 1 e não for Coupe, Trophée, Champions ou Destacado
                    if not is_ligue1 or is_coupe or is_trophee or is_champions or is_destacado or is_coupe_text:
                        continue
                    
                    # Busca todos os jogos dentro do card - aceita qualquer elemento com data-id
                    game_rows = card.query_selector_all('[data-id]')
                    
                    if debug:
                        print(f"  Found {len(game_rows)} elements with data-id in Ligue 1 card")
                    
                    for game_row in game_rows:
                        try:
                            game_text = game_row.inner_text()
                            game_html = game_row.inner_html()
                            
                            if debug:
                                print(f"    Checking element: {repr(game_text[:150])}")
                            
                            # Extrai data - aceita DD/MM/YY ou DD/MM/YYYY
                            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', game_text)
                            if not date_match:
                                if debug:
                                    print(f"      No date found, skipping")
                                continue
                            
                            date_str = date_match.group(1)
                            
                            # Filtrar apenas jogos de 2026
                            if not date_str.endswith("/26") and not date_str.endswith("/2026"):
                                if debug:
                                    print(f"      Not 2026, skipping")
                                continue
                            
                            # Normalizar data para DD/MM/YY
                            if date_str.endswith("/2026"):
                                date_str = date_str.replace("/2026", "/26")
                            
                            # Remover a data do texto para não confundir com o placar
                            text_without_date = game_text.replace(date_match.group(0), "")
                            
                            # Remover status do jogo (F2°T, FT, etc) que contém números
                            text_clean = re.sub(r'F\d+°T|FT|HT', '', text_without_date)
                            
                            # Extrair TODOS os números do texto limpo
                            all_numbers = re.findall(r'\d+', text_clean)
                            
                            if debug:
                                print(f"      All numbers found: {all_numbers}")
                            
                            # SofaScore retorna 4 números: [gols_casa, gols_casa_extra, gols_fora, gols_fora_extra]
                            # O placar real está nas posições 0 e 2
                            if len(all_numbers) < 4:
                                if debug:
                                    print(f"      Menos de 4 números encontrados ({len(all_numbers)}), pulando")
                                continue
                            
                            # Usar posições 0 e 2 para o placar correto
                            home_score = int(all_numbers[0])
                            away_score = int(all_numbers[2])
                            
                            # Extrai times - precisamos ser mais espertos aqui
                            # Remove caracteres especiais
                            clean_text = re.sub(r'[^\w\s\-/:]', '', game_text)
                            lines = clean_text.split('\n')
                            teams_found = []
                            
                            for line in lines:
                                line = line.strip()
                                # Ignora linhas com apenas números, datas, horas ou palavras curtas
                                if len(line) > 2:
                                    # Pula se for só números
                                    if re.match(r'^\d+$', line):
                                        continue
                                    # Pula se for data ou hora
                                    if '/' in line or ':' in line:
                                        continue
                                    # Pula se for hífen ou placar (formato X - Y)
                                    if line == '-' or re.match(r'^\d+\s*-\s*\d+$', line):
                                        continue
                                    # Pula palavras de resultado
                                    if line in ['Casa', 'Fora', 'Empate', 'Vitória', 'Derrota', 'V', 'E', 'D', 'W', 'L', 'F2T', 'FT', 'Finalizado', 'AP']:
                                        continue
                                    # Evita duplicatas
                                    if line not in teams_found:
                                        teams_found.append(line)
                            
                            if debug:
                                print(f"      Teams found: {teams_found}")
                            
                            if len(teams_found) >= 2:
                                home_team = teams_found[0]
                                away_team = teams_found[1]
                                
                                # Filtrar jogos com times que não estão na Ligue 1
                                # Lista de times que não são da Ligue 1 (Coupe de France, etc)
                                times_nao_ligue1 = ['US Chantilly', 'Chantilly', 'Hauts Lyonnais', 'Bourgoin-Jallieu']
                                if any(time in home_team for time in times_nao_ligue1) or any(time in away_team for time in times_nao_ligue1):
                                    if debug:
                                        print(f"    SKIP - Time não é da Ligue 1: {home_team} x {away_team}")
                                    continue
                                
                                # Criar assinatura única para o jogo (data + times)
                                jogo_signature = f"{date_str}|{home_team}|{away_team}"
                                
                                # Pular se já foi adicionado
                                if jogo_signature in jogos_vistos:
                                    if debug:
                                        print(f"    SKIP - Jogo duplicado: {home_team} x {away_team} ({date_str})")
                                    continue
                                
                                jogos_vistos.add(jogo_signature)
                                
                                jogo = {
                                    "data": date_str,
                                    "mandante": home_team,
                                    "visitante": away_team,
                                    "placar_mandante": home_score,
                                    "placar_visitante": away_score
                                }
                                
                                jogos_ligue1.append(jogo)
                                
                                if debug:
                                    print(f"    OK - Game: {home_team} {home_score} x {away_score} {away_team} ({date_str})")
                        
                        except Exception as e:
                            if debug:
                                print(f"    Error processing game row: {e}")
                            continue
                
                except Exception as e:
                    if debug:
                        print(f"  Error processing card {card_idx}: {e}")
                    continue
            
            # Retorna apenas os últimos 5 jogos da Ligue 1
            jogos = jogos_ligue1[:5]
            print(f"Encontrados {len(jogos)} jogos da Ligue 1 para {team_name}")
            
        except Exception as e:
            print(f"Erro ao buscar dados do SofaScore: {e}")
        
        finally:
            browser.close()
    
    return jogos


def scrape_all_teams_sofascore(debug=False):
    """
    Busca os últimos 5 jogos de todos os times da Ligue 1
    """
    all_matches = {}
    
    print("\n=== BUSCANDO DADOS DO SOFASCORE ===")
    for team_name, team_id in LIGUE1_TEAM_IDS.items():
        print(f"\nProcessando {team_name}...")
        matches = scrape_sofascore_last5(team_id, team_name, debug=debug)
        all_matches[team_name] = matches
        time.sleep(2)  # Pausa entre requisições
    
    return all_matches


if __name__ == "__main__":
    # Teste com um time específico
    print("=== TESTE SOFASCORE LIGUE 1 ===")
    team = "Paris Saint-Germain"
    team_id = LIGUE1_TEAM_IDS[team]
    matches = scrape_sofascore_last5(team_id, team, debug=True)
    
    print(f"\n=== Últimos jogos de {team} ===")
    for match in matches:
        print(f"{match['data']}: {match['mandante']} {match['placar_mandante']} x {match['placar_visitante']} {match['visitante']}")
