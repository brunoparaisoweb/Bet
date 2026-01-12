#!/usr/bin/env python3
"""
Scraper para ogol.com.br - Premier League
Busca histórico de confrontos diretos (H2H) entre dois times
"""
from playwright.sync_api import sync_playwright
import time

# IDs dos times da Premier League no ogol.com.br
OGOL_TEAM_IDS = {
    "Arsenal": 75,
    "Manchester City": 86,
    "Man City": 86,
    "Aston Villa": 76,
    "Liverpool": 85,
    "Brentford": 2600,
    "Newcastle": 89,
    "Manchester United": 87,
    "Man Utd": 87,
    "Chelsea": 81,
    "Fulham": 83,
    "Sunderland": 91,
    "Brighton": 2601,
    "Brighton & Hove Albion": 2601,
    "Everton": 82,
    "Crystal Palace": 2597,
    "Tottenham": 92,
    "Bournemouth": 4929,
    "Leeds United": 84,
    "Leeds": 84,
    "Nottingham Forest": 2579,
    "Forest": 2579,
    "West Ham": 94,
    "Burnley": 2580,
    "Wolverhampton": 1135,
    "Wolves": 1135
}

# Slugs dos times para URLs
OGOL_TEAM_SLUGS = {
    "Arsenal": "arsenal",
    "Manchester City": "manchester-city",
    "Aston Villa": "aston-villa",
    "Liverpool": "liverpool",
    "Brentford": "brentford",
    "Newcastle": "newcastle-united",
    "Manchester United": "manchester-united",
    "Chelsea": "chelsea",
    "Fulham": "fulham",
    "Sunderland": "sunderland",
    "Brighton": "brighton-hove-albion",
    "Brighton & Hove Albion": "brighton-hove-albion",
    "Everton": "everton",
    "Crystal Palace": "crystal-palace",
    "Tottenham": "tottenham-hotspur",
    "Bournemouth": "afc-bournemouth",
    "Leeds United": "leeds-united",
    "Nottingham Forest": "nottingham-forest",
    "West Ham": "west-ham-united",
    "Burnley": "burnley",
    "Wolverhampton": "wolverhampton-wanderers"
}

def normalizar_nome_time(nome):
    """Normaliza o nome do time para buscar no dicionário."""
    normalizacoes = {
        "Man City": "Manchester City",
        "Man Utd": "Manchester United",
        "Leeds": "Leeds United",
        "Forest": "Nottingham Forest",
        "Wolves": "Wolverhampton",
        "Brighton": "Brighton & Hove Albion"
    }
    
    return normalizacoes.get(nome, nome)

def scrape_h2h_ogol(time1, time2, debug=False):
    """
    Busca os últimos confrontos diretos entre time1 e time2 no ogol.com.br
    
    Returns:
        Lista de dicionários com informações dos jogos H2H
    """
    time1 = normalizar_nome_time(time1)
    time2 = normalizar_nome_time(time2)
    
    # Busca IDs
    id_time1 = OGOL_TEAM_IDS.get(time1)
    id_time2 = OGOL_TEAM_IDS.get(time2)
    
    if not id_time1 or not id_time2:
        print(f"ERRO: IDs não encontrados - {time1}: {id_time1}, {time2}: {id_time2}")
        return []
    
    # Busca slugs
    slug1 = OGOL_TEAM_SLUGS.get(time1)
    slug2 = OGOL_TEAM_SLUGS.get(time2)
    
    if not slug1 or not slug2:
        print(f"ERRO: Slugs não encontrados - {time1}: {slug1}, {time2}: {slug2}")
        return []
    
    jogos_h2h = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # URL do histórico de confrontos
            url = f"https://www.ogol.com.br/equipe/{slug1}/{id_time1}/historico-vs-equipes?fk_adv={id_time2}"
            
            if debug:
                print(f"Acessando: {url}")
            
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            # Busca a tabela de jogos
            linhas = page.query_selector_all("table.jogos tbody tr")
            
            if debug:
                print(f"Encontradas {len(linhas)} linhas na tabela H2H")
            
            for linha in linhas:
                try:
                    # Extrai todas as células
                    celulas = linha.query_selector_all("td")
                    
                    if len(celulas) < 5:
                        continue
                    
                    # Resultado (V, E, D)
                    resultado = celulas[0].inner_text().strip()
                    
                    # Data
                    data = celulas[1].inner_text().strip()
                    
                    # Informações do jogo (times e placar)
                    info_jogo = celulas[2].inner_text().strip()
                    
                    # Competição
                    competicao = celulas[3].inner_text().strip() if len(celulas) > 3 else ""
                    
                    # Monta texto do jogo
                    texto_jogo = f"{resultado} {data} {info_jogo}"
                    
                    jogos_h2h.append({
                        "texto": texto_jogo,
                        "resultado": resultado,
                        "data": data,
                        "jogo": info_jogo,
                        "competicao": competicao
                    })
                    
                    if debug:
                        print(f"  {texto_jogo}")
                
                except Exception as e:
                    if debug:
                        print(f"Erro ao processar linha: {e}")
                    continue
            
            # Retorna até 5 jogos mais recentes
            jogos_h2h = jogos_h2h[:5]
            
        except Exception as e:
            print(f"Erro ao buscar H2H: {e}")
        
        finally:
            browser.close()
    
    return jogos_h2h

if __name__ == "__main__":
    # Teste
    print("=== Testando scraper H2H - Premier League ===\n")
    
    confrontos_teste = [
        ("Arsenal", "Manchester City"),
        ("Liverpool", "Manchester United"),
        ("Chelsea", "Tottenham")
    ]
    
    for time1, time2 in confrontos_teste:
        print(f"\n--- {time1} vs {time2} ---")
        jogos = scrape_h2h_ogol(time1, time2, debug=True)
        print(f"Total de jogos H2H: {len(jogos)}")
