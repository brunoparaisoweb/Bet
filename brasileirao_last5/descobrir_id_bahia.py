#!/usr/bin/env python3
"""Acessa página do Bahia para descobrir ID"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    # Acessa página do Bahia
    url = "https://www.ogol.com.br/equipe/bahia/"
    print(f"Acessando: {url}\n")
    
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    time.sleep(5)
    
    # Procura por um link "histórico vs equipes" ou similar
    link = page.query_selector('a[href*="historico-vs-equipes"]')
    if link:
        href = link.get_attribute('href')
        print(f"Link histórico encontrado: {href}")
        
        # Clica no link
        link.click()
        time.sleep(3)
        
        # Pega a URL atual
        url_atual = page.url
        print(f"URL após clicar: {url_atual}")
        
        # O ID do Bahia estará na URL antes do ?fk_adv
        # Formato: /equipe/bahia/ID/historico-vs-equipes ou similar
        import re
        match = re.search(r'/equipe/bahia/(\d+)', url_atual)
        if match:
            id_bahia = match.group(1)
            print(f"\n✓ ID do Bahia: {id_bahia}")
    
    print("\nMantendo navegador aberto por 20 segundos...")
    time.sleep(20)
    browser.close()
