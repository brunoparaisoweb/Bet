from ogol_scraper import scrape_h2h_ogol, OGOL_TEAM_IDS, OGOL_TEAM_SLUGS

print('=== VERIFICANDO IDs E SLUGS ===')
print(f'Mirassol ID: {OGOL_TEAM_IDS.get("Mirassol")}')
print(f'Mirassol Slug: {OGOL_TEAM_SLUGS.get("Mirassol")}')
print(f'Vasco ID: {OGOL_TEAM_IDS.get("Vasco")}')
print(f'Vasco Slug: {OGOL_TEAM_SLUGS.get("Vasco")}')

print('\n=== BUSCANDO H2H MIRASSOL VS VASCO ===')
jogos = scrape_h2h_ogol('Mirassol', 'Vasco', debug=True)

print(f'\n\nTotal de jogos encontrados: {len(jogos)}')
if jogos:
    print('\nJogos:')
    for i, jogo in enumerate(jogos, 1):
        print(f'{i}. {jogo}')
else:
    print('Nenhum jogo encontrado!')
