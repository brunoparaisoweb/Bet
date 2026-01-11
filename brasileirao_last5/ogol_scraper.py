#!/usr/bin/env python3
"""
Scraper para buscar histórico de confrontos (H2H) no site ogol.com.br
"""

from playwright.sync_api import sync_playwright
import time

# Mapeamento de IDs dos times no ogol.com.br
# Formato: "Nome do Time": id_ogol
OGOL_TEAM_IDS = {
    "Flamengo": 2240,
    "São Paulo": 2256,
    "Vasco": 2258,
    "Fluminense": 2241,
    "Grêmio": 2243,
    "Botafogo": 2233,
    "Cruzeiro": 2236,
    "Corinthians": 2234,
    "Bahia": 2231,
    "Mirassol": 3348,
    "Palmeiras": 2248,
    "Atlético-MG": 2229,
    "Internacional": 2245,
    "Bragantino": 3156,
    "Vitória": 2259,
    "Santos": 2254,
    "Remo": 3423,
    "Chapecoense": 3195,
    "Coritiba": 2235,
    "Athletico-PR": 2230
}

# Mapeamento de slugs dos times no ogol.com.br
OGOL_TEAM_SLUGS = {
    "Flamengo": "flamengo",
    "São Paulo": "sao-paulo",
    "Vasco": "vasco-da-gama",
    "Fluminense": "fluminense",
    "Grêmio": "gremio",
    "Botafogo": "botafogo",
    "Cruzeiro": "cruzeiro",
    "Corinthians": "corinthians",
    "Bahia": "bahia",
    "Mirassol": "mirassol",
    "Palmeiras": "palmeiras",
    "Atlético-MG": "atletico-mineiro",
    "Internacional": "internacional",
    "Bragantino": "red-bull-bragantino",
    "Vitória": "vitoria",
    "Santos": "santos",
    "Remo": "clube-do-remo",
    "Chapecoense": "chapecoense",
    "Coritiba": "coritiba",
    "Athletico-PR": "athletico-paranaense"
}


def scrape_h2h_ogol(time1, time2, debug=False):
    """
    Busca os últimos 5 confrontos entre dois times no ogol.com.br
    
    Args:
        time1: Nome do primeiro time
        time2: Nome do segundo time
        debug: Se True, mostra mensagens de debug
        
    Returns:
        Lista com os últimos 5 confrontos entre os times
    """
    if time1 not in OGOL_TEAM_IDS or time2 not in OGOL_TEAM_IDS:
        if debug:
            print(f"Time não encontrado no mapeamento de IDs do ogol")
        return []
    
    if OGOL_TEAM_IDS[time1] is None or OGOL_TEAM_IDS[time2] is None:
        if debug:
            print(f"ID do time não configurado no ogol")
        return []
    
    slug1 = OGOL_TEAM_SLUGS[time1]
    id_time1 = OGOL_TEAM_IDS[time1]
    id_time2 = OGOL_TEAM_IDS[time2]
    
    # Monta a URL (inclui o ID do primeiro time)
    url = f"https://www.ogol.com.br/equipe/{slug1}/{id_time1}/historico-vs-equipes?fk_adv={id_time2}"
    
    if debug:
        print(f"\nBuscando H2H de {time1} vs {time2}")
        print(f"URL: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(5)
            
            if debug:
                print("Página carregada")
            
            # Extrai os jogos da tabela de histórico
            # A página do ogol tem uma tabela com os confrontos
            jogos = []
            
            # JavaScript para extrair os dados da tabela de forma mais estruturada
            js_code = """
            () => {
                const jogos = [];
                
                // Procura por linhas de tabela que contenham informações de jogos
                const linhas = document.querySelectorAll('tr');
                
                for (const linha of linhas) {
                    const colunas = linha.querySelectorAll('td');
                    
                    // Verifica se a linha tem dados de jogo (data, times, placar)
                    if (colunas.length >= 3) {
                        let textoCompleto = '';
                        
                        for (const col of colunas) {
                            const texto = (col.innerText || col.textContent || '').trim();
                            if (texto) {
                                textoCompleto += texto + ' ';
                            }
                        }
                        
                        textoCompleto = textoCompleto.trim();
                        
                        // Verifica se tem data no formato XX-XX-XXXX ou XX/XX/XXXX
                        if (textoCompleto.match(/\\d{4}-\\d{2}-\\d{2}/) || 
                            textoCompleto.match(/\\d{2}\\/\\d{2}\\/\\d{4}/)) {
                            jogos.push({
                                texto: textoCompleto
                            });
                        }
                    }
                }
                
                return jogos;
            }
            """
            
            jogos_extraidos = page.evaluate(js_code)
            
            if debug:
                print(f"\nEncontrados {len(jogos_extraidos)} jogos")
                for i, jogo in enumerate(jogos_extraidos[:10]):
                    print(f"  {i+1}. {jogo['texto'][:100]}")
            
            # Filtra e retorna os primeiros 5 jogos
            jogos = jogos_extraidos[:5]
            
            browser.close()
            return jogos
            
        except Exception as e:
            if debug:
                print(f"Erro ao buscar H2H: {e}")
            browser.close()
            return []


if __name__ == "__main__":
    # Teste com Fluminense vs Grêmio
    print("="*80)
    print("TESTE: Fluminense vs Grêmio")
    print("="*80)
    
    jogos = scrape_h2h_ogol("Fluminense", "Grêmio", debug=True)
    
    print(f"\n\nRESULTADO FINAL: {len(jogos)} jogos H2H encontrados")
    if jogos:
        print("\nJogos:")
        for i, jogo in enumerate(jogos, 1):
            print(f"{i}. {jogo['texto']}")
