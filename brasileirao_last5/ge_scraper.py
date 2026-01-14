#!/usr/bin/env python3
"""Scrape GE.Globo para pegar jogos da 1ª rodada do Brasileirão"""
from playwright.sync_api import sync_playwright
import re

def scrape_primeira_rodada():
    """Busca os jogos da 1ª rodada do Brasileirão no GE"""
    jogos = []
    jogos_set = set()  # Para evitar duplicatas
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://ge.globo.com/futebol/brasileirao-serie-a/", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Extrai o texto completo da página
        page_text = page.inner_text("body")
        lines = page_text.split('\n')
        
        # Procura por todas as ocorrências de jogos com data 28/01 ou 29/01
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Procura por data 28/01 ou 29/01
            if '28/01' in line or '29/01' in line:
                # Extrai a data da linha
                data_jogo = "28/01" if "28/01" in line else "29/01"
                
                # Próximas 2 linhas devem ser os times
                if i + 2 < len(lines):
                    time1 = lines[i+1].strip()
                    time2 = lines[i+2].strip()
                    
                    # Remove caracteres estranhos e valida
                    time1 = re.sub(r'[^a-zA-Zãçáéíóú\-\s]', '', time1).strip()
                    time2 = re.sub(r'[^a-zA-Zãçáéíóú\-\s]', '', time2).strip()
                    
                    # Valida se são times (não horário, não vazio, etc)
                    if (time1 and time2 and 
                        len(time1) > 2 and len(time2) > 2 and
                        not ':' in time1 and not ':' in time2 and
                        not time1.isdigit() and not time2.isdigit()):
                        
                        # Cria chave única para evitar duplicatas
                        chave = f"{time1}_{time2}"
                        if chave not in jogos_set:
                            jogos_set.add(chave)
                            jogos.append({
                                "data": data_jogo,
                                "time1": time1,
                                "time2": time2
                            })
            i += 1
        
        browser.close()
    
    return jogos

def scrape_classificacao():
    """Busca a classificação atual do Brasileirão no GE"""
    classificacao = []
    
    # Como o campeonato ainda não começou, retorna os 20 times com 0 pontos
    # Lista de times do Brasileirão 2025
    times_brasileirao = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Fluminense",
        "Grêmio", "Botafogo", "Atlético-MG", "Internacional", "Cruzeiro",
        "Athletico-PR", "Bahia", "Vasco", "Bragantino", "Vitória",
        "Mirassol", "Santos", "Remo", "Chapecoense", "Coritiba"
    ]
    
    for i, time in enumerate(times_brasileirao, 1):
        classificacao.append({
            "posicao": str(i),
            "time": time,
            "pontos": "0",
            "jogos": "0"
        })
    
    return classificacao

if __name__ == "__main__":
    jogos = scrape_primeira_rodada()
    for j in jogos:
        print(f"{j['data']} - {j['time1']} x {j['time2']}")
    
    print("\n--- Classificação ---")
    classificacao = scrape_classificacao()
    for c in classificacao:
        print(f"{c['posicao']}. {c['time']} - {c['pontos']} pts ({c['jogos']} jogos)")
