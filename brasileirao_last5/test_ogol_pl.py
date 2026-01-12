#!/usr/bin/env python3
"""
Teste do scraper ogol.com.br para Premier League
"""
from ogol_scraper_pl import scrape_h2h_ogol

# Testa alguns confrontos da Premier League
confrontos_teste = [
    ("Arsenal", "Liverpool"),
    ("Manchester City", "Chelsea"),
    ("Tottenham", "Manchester United")
]

print("=== TESTANDO OGOL SCRAPER - PREMIER LEAGUE ===\n")

for time1, time2 in confrontos_teste:
    print(f"\n--- {time1} vs {time2} ---")
    try:
        resultado = scrape_h2h_ogol(time1, time2, debug=True)
        
        if resultado:
            print(f"[OK] Confronto encontrado!")
            print(f"  Total de jogos: {resultado.get('total_jogos', 0)}")
            print(f"  Vitorias {time1}: {resultado.get('vitorias_time1', 0)}")
            print(f"  Empates: {resultado.get('empates', 0)}")
            print(f"  Vitorias {time2}: {resultado.get('vitorias_time2', 0)}")
        else:
            print(f"[X] Nenhum dado encontrado")
    except Exception as e:
        print(f"[X] Erro: {e}")

print("\n" + "="*50)
print("Teste concluído")
