#!/usr/bin/env python3
"""Debug GE.Globo para ver todos os jogos da primeira rodada"""
from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://ge.globo.com/futebol/brasileirao-serie-a/", timeout=30000)
    page.wait_for_timeout(5000)
    
    # Extrai o texto completo da página
    page_text = page.inner_text("body")
    
    # Salva para análise
    with open("ge_debug.txt", "w", encoding="utf-8") as f:
        f.write(page_text)
    
    print("Texto da página salvo em ge_debug.txt")
    
    # Procura por todas as ocorrências de "28/01"
    lines = page_text.split('\n')
    print("\n=== Linhas com 28/01 ===")
    for i, line in enumerate(lines):
        if '28/01' in line:
            # Mostra contexto (5 linhas antes e depois)
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            print(f"\n--- Contexto linha {i} ---")
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{j}: {lines[j]}")
    
    browser.close()
