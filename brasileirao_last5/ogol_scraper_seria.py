#!/usr/bin/env python3
"""
Scraper para ogol.com.br - Serie A
Busca histórico de confrontos diretos (H2H) entre dois times
"""
from playwright.sync_api import sync_playwright
import time

# IDs dos times da Serie A no ogol.com.br
SERIA_OGOL_IDS = {
    "Internazionale": 63,
    "Inter": 63,
    "Milan": 66,
    "Napoli": 3735,
    "Roma": 72,
    "Juventus": 64,
    "Como": 61,
    "Como 1907": 61,
    "Atalanta": 57,
    "Bologna": 58,
    "Lazio": 65,
    "Udinese": 74,
    "Sassuolo": 7908,
    "Cremonese": 3725,
    "Parma": 68,
    "Torino": 73,
    "Cagliari": 3720,
    "Genoa": 3728,
    "Fiorentina": 3726,
    "Lecce": 1129,
    "Pisa": 3740,
    "Hellas Verona": 3751,
    "Verona": 3751
}


# Slugs dos times para URLs
OGOL_TEAM_SLUGS = {
    "Internazionale": "internazionale",
    "Inter": "internazionale",
    "Milan": "milan",
    "Napoli": "napoli",
    "Roma": "roma",
    "Juventus": "juventus",
    "Como": "como",
    "Como 1907": "como",
    "Atalanta": "atalanta",
    "Bologna": "bologna",
    "Lazio": "lazio",
    "Udinese": "udinese",
    "Sassuolo": "sassuolo",
    "Cremonese": "cremonese",
    "Parma": "parma",
    "Torino": "torino",
    "Cagliari": "cagliari",
    "Genoa": "genoa",
    "Fiorentina": "fiorentina",
    "Lecce": "lecce",
    "Pisa": "pisa",
    "Hellas Verona": "hellas-verona",
    "Verona": "hellas-verona"
}

def normalizar_nome_time(nome):
    """Normaliza o nome do time para buscar no dicionário."""
    normalizacoes = {
        "Inter": "Internazionale",
        "Como 1907": "Como",
        "Verona": "Hellas Verona"
    }
    
    return normalizacoes.get(nome, nome)

def scrape_h2h_ogol_seria(time1, time2, debug=False):
    """
    Busca os últimos confrontos diretos entre time1 e time2 no ogol.com.br
    
    Returns:
        Lista de dicionários com informações dos jogos H2H
    """
    time1 = normalizar_nome_time(time1)
    time2 = normalizar_nome_time(time2)
    
    # Busca IDs
    id_time1 = SERIA_OGOL_IDS.get(time1)
    id_time2 = SERIA_OGOL_IDS.get(time2)
    
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
            
            # Busca a tabela de jogos - estrutura atualizada do ogol
            linhas = page.query_selector_all("table.zztable.stats tbody tr.parent")
            
            if debug:
                print(f"Encontradas {len(linhas)} linhas na tabela H2H")
            
            for linha in linhas:
                try:
                    # Extrai as células
                    celulas = linha.query_selector_all("td")
                    
                    if len(celulas) < 7:
                        continue
                    
                    # Estrutura: form | data | time casa | logo | resultado | logo | time visitante | rodada | competição
                    # Resultado (V, E, D) - está na primeira célula
                    resultado_elem = celulas[0].query_selector("div.sign")
                    if resultado_elem:
                        resultado_class = resultado_elem.get_attribute("class")
                        if "victory" in resultado_class or "win" in resultado_class:
                            resultado = "V"
                        elif "draw" in resultado_class:
                            resultado = "E"
                        elif "loss" in resultado_class or "defeat" in resultado_class:
                            resultado = "D"
                        else:
                            resultado = resultado_elem.inner_text().strip()
                    else:
                        resultado = ""
                    
                    # Data
                    data = celulas[1].inner_text().strip()
                    
                    # Times e placar
                    time_casa = celulas[2].inner_text().strip()
                    placar = celulas[4].inner_text().strip()
                    time_visitante = celulas[6].inner_text().strip()
                    
                    # Competição (se houver)
                    competicao = celulas[8].inner_text().strip() if len(celulas) > 8 else ""
                    
                    # Monta informação do jogo
                    info_jogo = f"{time_casa} {placar} {time_visitante}"
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
    print("=== Testando scraper H2H - Serie A ===\n")
    
    confrontos_teste = [
        ("Internazionale", "Milan"),
        ("Juventus", "Napoli"),
        ("Roma", "Atalanta")
    ]
    
    for time1, time2 in confrontos_teste:
        print(f"\n--- {time1} vs {time2} ---")
        jogos = scrape_h2h_ogol_seria(time1, time2, debug=True)
        print(f"Total de jogos H2H: {len(jogos)}")

