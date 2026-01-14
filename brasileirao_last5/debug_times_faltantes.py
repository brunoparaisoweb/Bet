#!/usr/bin/env python3
"""Debug para encontrar todos os 20 times"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://ge.globo.com/futebol/brasileirao-serie-a/", timeout=30000)
    page.wait_for_timeout(3000)
    
    # Extrai o texto completo
    page_text = page.inner_text("body")
    
    # Times esperados
    times_esperados = [
        "CAM", "ATL", "Atlético", "Atletico",
        "INT", "Internacional",
        "CAP", "Athletico",
        "CFC", "Coritiba",
        "RBB", "Bragantino",
        "VIT", "Vitória", "Vitoria",
        "REM", "Remo",
        "FLU", "Fluminense",
        "GRE", "Grêmio", "Gremio",
        "MIR", "Mirassol",
        "VAS", "Vasco",
        "CHA", "Chapecoense",
        "SAN", "Santos",
        "SAO", "São Paulo", "Sao Paulo",
        "FLA", "Flamengo",
        "PAL", "Palmeiras",
        "BOT", "Botafogo",
        "CRU", "Cruzeiro",
        "COR", "Corinthians",
        "BAH", "Bahia"
    ]
    
    print("=== Procurando times no texto ===")
    for time in times_esperados:
        count = page_text.count(time)
        if count > 0:
            print(f"{time}: {count} ocorrências")
    
    # Salva o texto para análise
    with open("ge_full_text.txt", "w", encoding="utf-8") as f:
        f.write(page_text)
    
    print("\nTexto completo salvo em ge_full_text.txt")
    
    # Procura especificamente por Botafogo e Cruzeiro
    print("\n=== Contexto de Botafogo ===")
    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        if 'Botafogo' in line or 'BOT' in line:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            print(f"\nLinha {i}:")
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{lines[j]}")
    
    print("\n=== Contexto de Cruzeiro ===")
    for i, line in enumerate(lines):
        if 'Cruzeiro' in line or 'CRU' in line:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            print(f"\nLinha {i}:")
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{lines[j]}")
    
    browser.close()
