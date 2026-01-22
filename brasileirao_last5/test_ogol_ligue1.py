# -*- coding: utf-8 -*-
import asyncio
from ogol_scraper_ligue1 import scrape_h2h_ogol_ligue1

async def test():
    result = await scrape_h2h_ogol_ligue1('Lille', 'Strasbourg', debug=True)
    print('\n=== RESULTADO FINAL ===')
    print(f'Jogos H2H: {len(result)}')
    for i, m in enumerate(result, 1):
        print(f'{i}. {m}')
    return result

if __name__ == "__main__":
    asyncio.run(test())
