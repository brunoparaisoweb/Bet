#!/usr/bin/env python3
"""
Scraper para GE - Premier League
Busca jogos da próxima rodada e classificação atual
"""
from playwright.sync_api import sync_playwright
import time

def normalizar_nome_time(nome_raw, img_src=""):
    """Normaliza o nome do time, tratando casos especiais da Premier League."""
    nome = nome_raw.strip()
    
    # Casos especiais baseados no prefixo do nome
    if nome.startswith("Manchester"):
        # Verifica pela imagem
        if "manchester-city" in img_src.lower():
            return "Manchester City"
        elif "manchester-united" in img_src.lower():
            return "Manchester United"
        # Se não tem imagem, tenta pelo nome completo
        elif "City" in nome:
            return "Manchester City"
        elif "United" in nome:
            return "Manchester United"
    
    if nome.startswith("Wolverham"):
        return "Wolverhampton"
    
    if nome.startswith("Bournemo"):
        return "Bournemouth"
    
    if nome.startswith("Nottingha"):
        return "Nottingham Forest"
    
    if nome.startswith("Crystal Pala"):
        return "Crystal Palace"
    
    # Outros casos conhecidos
    normalizacoes = {
        "Brighton": "Brighton",
        "Leeds": "Leeds United",
        "Forest": "Nottingham Forest",
        "Wolves": "Wolverhampton",
        "Man City": "Manchester City",
        "Man Utd": "Manchester United",
    }
    
    for key, value in normalizacoes.items():
        if key in nome:
            return value
    
    return nome

def scrape_primeira_rodada():
    """Busca os jogos da próxima rodada da Premier League."""
    jogos = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Acessando página do GE - Premier League...")
            page.goto("https://ge.globo.com/futebol/futebol-internacional/futebol-ingles/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            # Busca os jogos da próxima rodada
            jogos_elements = page.query_selector_all(".proximos-jogos__lista .proximos-jogos__item")
            
            if not jogos_elements:
                print("Nenhum jogo encontrado na próxima rodada")
                return jogos
            
            print(f"Encontrados {len(jogos_elements)} jogos")
            
            for elem in jogos_elements:
                try:
                    # Data e hora
                    data_elem = elem.query_selector(".proximos-jogos__data")
                    data = data_elem.inner_text().strip() if data_elem else "Data não encontrada"
                    
                    # Time mandante
                    time1_elem = elem.query_selector(".equipes__nome--mandante")
                    time1_text = time1_elem.inner_text().strip() if time1_elem else ""
                    
                    # Busca imagem do time mandante para identificar Manchester City/United
                    img_mandante = elem.query_selector(".equipes__escudo--mandante")
                    img_mandante_src = img_mandante.get_attribute("src") if img_mandante else ""
                    
                    time1 = normalizar_nome_time(time1_text, img_mandante_src)
                    
                    # Time visitante
                    time2_elem = elem.query_selector(".equipes__nome--visitante")
                    time2_text = time2_elem.inner_text().strip() if time2_elem else ""
                    
                    # Busca imagem do time visitante
                    img_visitante = elem.query_selector(".equipes__escudo--visitante")
                    img_visitante_src = img_visitante.get_attribute("src") if img_visitante else ""
                    
                    time2 = normalizar_nome_time(time2_text, img_visitante_src)
                    
                    if time1 and time2:
                        jogos.append({
                            "data": data,
                            "time1": time1,
                            "time2": time2
                        })
                        print(f"  {data}: {time1} x {time2}")
                
                except Exception as e:
                    print(f"Erro ao processar jogo: {e}")
                    continue
        
        except Exception as e:
            print(f"Erro ao acessar página: {e}")
        
        finally:
            browser.close()
    
    return jogos

def scrape_classificacao():
    """Busca a classificação atual da Premier League."""
    classificacao = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Acessando classificação da Premier League...")
            page.goto("https://ge.globo.com/futebol/futebol-internacional/futebol-ingles/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            # Busca a tabela de classificação
            linhas = page.query_selector_all(".tabela-times tbody tr")
            
            if not linhas:
                print("Tabela de classificação não encontrada")
                return classificacao
            
            print(f"Encontradas {len(linhas)} posições na tabela")
            
            for linha in linhas:
                try:
                    # Posição
                    pos_elem = linha.query_selector(".tabela-times__posicao")
                    posicao = pos_elem.inner_text().strip() if pos_elem else ""
                    
                    # Nome do time
                    time_elem = linha.query_selector(".tabela-times__nome")
                    time_text = time_elem.inner_text().strip() if time_elem else ""
                    
                    # Busca imagem para identificar Manchester City/United
                    img_elem = linha.query_selector(".tabela-times__escudo")
                    img_src = img_elem.get_attribute("src") if img_elem else ""
                    
                    time = normalizar_nome_time(time_text, img_src)
                    
                    # Pontos
                    pontos_elem = linha.query_selector(".tabela-times__pontos")
                    pontos = pontos_elem.inner_text().strip() if pontos_elem else "0"
                    
                    # Jogos
                    jogos_elem = linha.query_selector(".tabela-times__jogos")
                    jogos = jogos_elem.inner_text().strip() if jogos_elem else "0"
                    
                    if posicao and time:
                        classificacao.append({
                            "posicao": posicao,
                            "time": time,
                            "pontos": pontos,
                            "jogos": jogos
                        })
                        print(f"  {posicao}º {time} - {pontos} pts ({jogos} jogos)")
                
                except Exception as e:
                    print(f"Erro ao processar linha da tabela: {e}")
                    continue
        
        except Exception as e:
            print(f"Erro ao acessar classificação: {e}")
        
        finally:
            browser.close()
    
    return classificacao

if __name__ == "__main__":
    print("=== Testando scraper GE - Premier League ===\n")
    
    print("\n--- PRÓXIMA RODADA ---")
    jogos = scrape_primeira_rodada()
    print(f"\nTotal de jogos: {len(jogos)}")
    
    print("\n--- CLASSIFICAÇÃO ---")
    classificacao = scrape_classificacao()
    print(f"\nTotal de times: {len(classificacao)}")
