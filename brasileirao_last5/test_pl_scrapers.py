#!/usr/bin/env python3
"""
Teste básico de scraping da Premier League
"""
from ge_scraper_pl import scrape_primeira_rodada, scrape_classificacao

print("=== TESTANDO SCRAPERS PREMIER LEAGUE ===\n")

print("1. Buscando próxima rodada...")
try:
    jogos = scrape_primeira_rodada()
    print(f"✓ Encontrados {len(jogos)} jogos")
    if jogos:
        for jogo in jogos[:3]:
            print(f"  {jogo['data']}: {jogo['time1']} x {jogo['time2']}")
except Exception as e:
    print(f"✗ Erro: {e}")

print("\n2. Buscando classificação...")
try:
    classificacao = scrape_classificacao()
    print(f"✓ Encontrados {len(classificacao)} times")
    if classificacao:
        for pos in classificacao[:5]:
            print(f"  {pos['posicao']}º {pos['time']} - {pos['pontos']} pts")
except Exception as e:
    print(f"✗ Erro: {e}")

print("\n✓ Testes concluídos!")
