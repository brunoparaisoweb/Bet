#!/usr/bin/env python3
"""
Teste rápido para verificar H2H entre dois times específicos
"""
from ogol_scraper_pl import scrape_h2h_ogol

# Testa um confronto da próxima rodada
print("=== Testando H2H: Arsenal vs Nottingham Forest ===\n")

jogos = scrape_h2h_ogol("Nottingham Forest", "Arsenal", debug=True)

print(f"\nTotal de jogos encontrados: {len(jogos)}")
print("\nÚltimos 5 jogos (do ponto de vista do Nottingham Forest):")
for i, jogo in enumerate(jogos[:5], 1):
    print(f"{i}. {jogo['resultado']} - {jogo['data']} - {jogo['jogo']}")
