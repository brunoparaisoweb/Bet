#!/usr/bin/env python3
"""
Testa o novo formato de URL
"""

from ogol_scraper import scrape_h2h_ogol

# Testa Mirassol vs Vasco
print("Testando Mirassol vs Vasco...")
resultado = scrape_h2h_ogol("Mirassol", "Vasco", debug=True)

if resultado:
    print(f"\n✓ Sucesso! Encontrados {len(resultado)} jogos:")
    for i, jogo in enumerate(resultado, 1):
        print(f"{i}. {jogo['texto']}")
else:
    print("\n✗ Nenhum jogo encontrado")
