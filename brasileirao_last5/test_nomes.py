from ge_scraper import scrape_primeira_rodada

jogos = scrape_primeira_rodada()
print("Jogos da rodada:")
for j in jogos[:3]:
    print(f'  "{j["time1"]}" vs "{j["time2"]}"')
    print(f'  Repr: {repr(j["time1"])} vs {repr(j["time2"])}')
