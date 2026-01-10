#!/usr/bin/env python3
"""Scrape GE.Globo para pegar jogos da 1ª rodada do Brasileirão"""
from playwright.sync_api import sync_playwright
import re

def scrape_primeira_rodada():
    """Busca os jogos da 1ª rodada do Brasileirão no GE"""
    jogos = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://ge.globo.com/futebol/brasileirao-serie-a/", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Extrai o HTML completo
        html = page.content()
        
        # Procura por jogos com data 28/01
        # Padrão: time1 vs time2
        jogos_texto = re.findall(r'28/01.*?([A-Z][a-zãçáéíóú\-]+(?:\s+[A-Z][a-zãçáéíóú\-]+)?)\s*!\[.*?\]\(.*?\).*?!\[.*?\]\(.*?\)\s*([A-Z][a-zãçáéíóú\-]+(?:\s+[A-Z][a-zãçáéíóú\-]+)?)', html, re.DOTALL)
        
        # Extrai times de forma mais simples
        page_text = page.inner_text("body")
        lines = page_text.split('\n')
        
        current_date = None
        for i, line in enumerate(lines):
            line = line.strip()
            # Procura por data 28/01
            if '28/01' in line and 'Quarta' in line:
                current_date = "28/01"
                # Próximas 2 linhas devem ser os times
                if i + 2 < len(lines):
                    time1 = lines[i+1].strip()
                    time2 = lines[i+2].strip()
                    # Remove caracteres estranhos e valida
                    time1 = re.sub(r'[^a-zA-Zãçáéíóú\-\s]', '', time1).strip()
                    time2 = re.sub(r'[^a-zA-Zãçáéíóú\-\s]', '', time2).strip()
                    
                    if time1 and time2 and len(time1) > 2 and len(time2) > 2:
                        jogos.append({
                            "data": "28/01",
                            "time1": time1,
                            "time2": time2
                        })
        
        browser.close()
    
    return jogos

if __name__ == "__main__":
    jogos = scrape_primeira_rodada()
    for j in jogos:
        print(f"{j['data']} - {j['time1']} x {j['time2']}")
