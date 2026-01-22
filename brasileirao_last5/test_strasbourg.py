#!/usr/bin/env python3
"""
Teste específico para o Strasbourg
"""
from sofascore_scraper_ligue1 import scrape_sofascore_last5

print("=== Testando Strasbourg ===")
print("ID SofaScore: 1659")
print()

jogos = scrape_sofascore_last5(1659, "Strasbourg", debug=True)

print(f"\n=== RESULTADO FINAL ===")
print(f"Total de jogos: {len(jogos)}")
for i, jogo in enumerate(jogos, 1):
    print(f"{i}. {jogo['data']} - {jogo['mandante']} {jogo['placar_mandante']} x {jogo['placar_visitante']} {jogo['visitante']}")
