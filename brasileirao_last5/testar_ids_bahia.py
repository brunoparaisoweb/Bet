#!/usr/bin/env python3
"""Testa IDs para encontrar o correto do Bahia"""

from ogol_scraper import scrape_h2h_ogol, OGOL_TEAM_IDS, OGOL_TEAM_SLUGS
from playwright.sync_api import sync_playwright
import time

# Vou testar manualmente acessando a URL
# https://www.ogol.com.br/equipe/corinthians/historico-vs-equipes?fk_adv=X
# e ver qual X mostra Bahia

ids_teste = range(2230, 2260)  # Testa IDs próximos aos conhecidos

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    for id_teste in ids_teste:
        url = f"https://www.ogol.com.br/equipe/corinthians/historico-vs-equipes?fk_adv={id_teste}"
        
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            time.sleep(1)
            
            # Pega o título ou nome da página
            titulo = page.title()
            
            # Procura por "Bahia" no título ou conteúdo
            conteudo = page.content()
            
            if "bahia" in titulo.lower() or "Bahia" in conteudo[:2000]:
                print(f"✓ ID {id_teste}: BAHIA ENCONTRADO!")
                print(f"  Título: {titulo}")
                print(f"  URL: {url}")
                break
        except:
            continue
    
    browser.close()
