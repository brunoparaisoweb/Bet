#!/usr/bin/env python3
"""Testa Corinthians vs Bahia no ogol"""

from ogol_scraper import scrape_h2h_ogol

print("="*80)
print("TESTE: Corinthians vs Bahia")
print("="*80)

jogos = scrape_h2h_ogol("Corinthians", "Bahia", debug=True)

print(f"\n\nRESULTADO FINAL: {len(jogos)} jogos H2H encontrados")
if jogos:
    print("\nJogos:")
    for i, jogo in enumerate(jogos, 1):
        print(f"{i}. {jogo['texto']}")
