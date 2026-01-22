# -*- coding: utf-8 -*-
"""
Scraper para buscar histórico de confrontos diretos (H2H) da Ligue 1 no OGol
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# Mapeamento de IDs dos times da Ligue 1 no OGol
LIGUE1_OGOL_IDS = {
    "Lens": 119,
    "Paris Saint-Germain": 127,
    "Olympique de Marselha": 122,
    "Lyon": 121,
    "Lille": 120,
    "Rennes": 128,
    "Strasbourg": 131,
    "Toulouse": 1140,
    "Monaco": 123,
    "Brest": 3840,
    "Angers": 3828,
    "Lorient": 3859,
    "Paris FC": 3852,
    "Le Havre": 118,
    "Nice": 126,
    "Nantes": 125,
    "Auxerre": 114,
    "Metz": 1139
}

# Slugs dos times para construção de URLs
OGOL_TEAM_SLUGS = {
    "Lens": "lens",
    "Paris Saint-Germain": "psg",
    "Olympique de Marselha": "marseille",
    "Lyon": "lyon",
    "Lille": "lille",
    "Rennes": "rennes",
    "Strasbourg": "strasbourg",
    "Toulouse": "toulouse",
    "Monaco": "monaco",
    "Brest": "brest",
    "Angers": "angers",
    "Lorient": "lorient",
    "Paris FC": "paris-fc",
    "Le Havre": "le-havre",
    "Nice": "nice",
    "Nantes": "nantes",
    "Auxerre": "auxerre",
    "Metz": "metz"
}

def normalizar_nome_time(nome):
    """
    Normaliza variações de nomes de times
    """
    normalizacoes = {
        "PSG": "Paris Saint-Germain",
        "Marseille": "Olympique de Marselha",
        "Paris": "Paris FC"
    }
    return normalizacoes.get(nome, nome)

async def scrape_h2h_ogol_ligue1(team1_name, team2_name, debug=False):
    """
    Busca o histórico de confrontos diretos entre duas equipes da Ligue 1 no OGol
    Retorna os ÚLTIMOS 5 confrontos, independente da temporada
    """
    # Normalizar nomes
    team1_name = normalizar_nome_time(team1_name)
    team2_name = normalizar_nome_time(team2_name)
    
    # Buscar IDs
    team1_id = LIGUE1_OGOL_IDS.get(team1_name)
    team2_id = LIGUE1_OGOL_IDS.get(team2_name)
    
    if team1_id is None or team2_id is None:
        print(f"ERRO: IDs não encontrados - {team1_name}: {team1_id}, {team2_name}: {team2_id}")
        return []
    
    # Buscar slugs
    team1_slug = OGOL_TEAM_SLUGS.get(team1_name)
    team2_slug = OGOL_TEAM_SLUGS.get(team2_name)
    
    if not team1_slug or not team2_slug:
        print(f"ERRO: Slugs não encontrados - {team1_name}: {team1_slug}, {team2_name}: {team2_slug}")
        return []
    
    # URL correta do confronto direto - histórico completo
    # Formato: equipe/{team_slug}/{team_id}/historico-vs-equipes?fk_adv={opponent_id}
    url = f"https://www.ogol.com.br/equipe/{team1_slug}/{team1_id}/historico-vs-equipes?fk_adv={team2_id}"
    
    print(f"\nBuscando H2H: {team1_name} vs {team2_name}")
    print(f"URL: {url}")
    
    matches = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(5000)
            
            # Salvar HTML para debug
            if debug:
                html_content = await page.content()
                debug_file = f"ogol_ligue1_h2h_{team1_name.replace(' ', '_')}_vs_{team2_name.replace(' ', '_')}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Debug HTML salvo em: {debug_file}")
            
            # Extrair dados usando JavaScript - similar ao scraper do brasileirão
            js_code = """
            () => {
                const jogos = [];
                const linhas = document.querySelectorAll('tr');
                
                for (const linha of linhas) {
                    const colunas = linha.querySelectorAll('td');
                    
                    if (colunas.length >= 3) {
                        let textoCompleto = '';
                        
                        for (const col of colunas) {
                            const texto = (col.innerText || col.textContent || '').trim();
                            if (texto) {
                                textoCompleto += texto + ' ';
                            }
                        }
                        
                        textoCompleto = textoCompleto.trim();
                        
                        // Verifica se tem data (dd/mm/yyyy ou dd mmm yyyy)
                        if (textoCompleto.match(/\\d{1,2}\\/\\d{1,2}\\/\\d{4}/) ||
                            textoCompleto.match(/\\d{4}-\\d{2}-\\d{2}/) ||
                            textoCompleto.match(/\\d{1,2}\\s+\\w{3}\\s+\\d{4}/)) {
                            jogos.push({
                                texto: textoCompleto
                            });
                        }
                    }
                }
                
                return jogos;
            }
            """
            
            jogos_extraidos = await page.evaluate(js_code)
            print(f"Extraídos {len(jogos_extraidos)} jogos da tabela")
            
            if debug and jogos_extraidos:
                print("Primeiros jogos encontrados:")
                for i, jogo in enumerate(jogos_extraidos[:10]):
                    print(f"  {i+1}. {jogo['texto'][:120]}")
            
            # Processar cada jogo extraído
            import re
            for idx, jogo_data in enumerate(jogos_extraidos):
                try:
                    texto = jogo_data['texto']
                    
                    if debug and idx < 3:
                        print(f"\n=== Processando jogo {idx+1} ===")
                        print(f"Texto original: '{texto[:150]}'")
                    
                    # Formato comum do OGol: "D 2025-11-09 Strasbourg 2-0 Lille R12 Campeonato..."
                    # ou "V 2024-04-21 Lille 1-0 Strasbourg R30 Campeonato..."
                    
                    # Tentar extrair data (formato YYYY-MM-DD ou DD/MM/YYYY)
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})', texto)
                    if not date_match:
                        if debug and idx < 3:
                            print("  ✗ Data não encontrada")
                        continue
                    data = date_match.group(1)
                    if debug and idx < 3:
                        print(f"  ✓ Data: {data}")
                    
                    # Remover a data e o resultado inicial (V/E/D) do texto ANTES de buscar o placar
                    texto_sem_data = re.sub(r'^[VED]\s+', '', texto)  # Remove V/E/D inicial
                    texto_sem_data = texto_sem_data.replace(data, '').strip()
                    
                    if debug and idx < 3:
                        print(f"  Texto sem data: '{texto_sem_data[:100]}'")
                    
                    # AGORA buscar o placar no texto sem data
                    score_match = re.search(r'\b(\d+)\s*-\s*(\d+)\b', texto_sem_data)
                    if not score_match:
                        if debug and idx < 3:
                            print("  ✗ Placar não encontrado")
                        continue
                    
                    placar_mandante = int(score_match.group(1))
                    placar_visitante = int(score_match.group(2))
                    placar_str = score_match.group(0)
                    if debug and idx < 3:
                        print(f"  ✓ Placar: {placar_mandante}-{placar_visitante}")
                    
                    # Agora temos algo como: "Strasbourg 2-0 Lille R12 Campeonato..."
                    # Dividir pelo placar
                    partes = texto_sem_data.split(placar_str, 1)
                    
                    if debug and idx < 3:
                        print(f"  Partes divididas: {len(partes)} - {[p[:50] for p in partes]}")
                    
                    if len(partes) >= 2:
                        mandante_raw = partes[0].strip()
                        resto = partes[1].strip()
                        
                        if debug and idx < 3:
                            print(f"  Mandante raw: '{mandante_raw}'")
                            print(f"  Resto: '{resto[:50]}'")
                        
                        # O visitante é a primeira palavra/time depois do placar
                        # "Lille R12 Campeonato..." -> pegar "Lille"
                        visitante_match = re.match(r'^(\S+(?:\s+\S+)?)', resto)
                        visitante = visitante_match.group(1).strip() if visitante_match else ""
                        
                        # Limpar o mandante (remover códigos extras)
                        mandante = mandante_raw.split()[0] if mandante_raw else ""
                        
                        # Limpar visitante (pode ter 2 palavras como "Paris Saint-Germain")
                        # mas geralmente o OGol usa nomes curtos
                        visitante_parts = visitante.split()
                        if visitante_parts:
                            visitante = visitante_parts[0]
                        
                        if debug and idx < 3:
                            print(f"  Times finais - Mandante: '{mandante}', Visitante: '{visitante}'")
                        
                        # Validar que temos times válidos
                        if mandante and visitante and len(mandante) > 1 and len(visitante) > 1:
                            # Calcular resultado do ponto de vista do team1 (mandante da busca)
                            # Normalizar nomes dos times para comparação
                            team1_norm = normalizar_nome_time(team1_name).lower()
                            mandante_norm = normalizar_nome_time(mandante).lower()
                            visitante_norm = normalizar_nome_time(visitante).lower()
                            
                            # Determinar se team1 foi mandante ou visitante neste jogo
                            if team1_norm in mandante_norm or mandante_norm in team1_norm:
                                # team1 foi mandante
                                if placar_mandante > placar_visitante:
                                    resultado = 'V'
                                elif placar_mandante < placar_visitante:
                                    resultado = 'D'
                                else:
                                    resultado = 'E'
                            elif team1_norm in visitante_norm or visitante_norm in team1_norm:
                                # team1 foi visitante
                                if placar_visitante > placar_mandante:
                                    resultado = 'V'
                                elif placar_visitante < placar_mandante:
                                    resultado = 'D'
                                else:
                                    resultado = 'E'
                            else:
                                resultado = '-'
                            
                            match = {
                                "data": data,
                                "mandante": mandante,
                                "visitante": visitante,
                                "placar_mandante": placar_mandante,
                                "placar_visitante": placar_visitante,
                                "resultado": resultado
                            }
                            matches.append(match)
                            if debug:
                                print(f"  ✓ {data}: {mandante} {placar_mandante} x {placar_visitante} {visitante} [{resultado}]")
                
                except Exception as e:
                    if debug:
                        print(f"Erro ao processar jogo '{texto[:80]}...': {e}")
                        import traceback
                        traceback.print_exc()
                    continue
            
            # Limitar aos últimos 5 confrontos
            matches = matches[:5]
            print(f"Total de jogos H2H (últimos 5): {len(matches)}")
            
        except Exception as e:
            print(f"Erro ao acessar página: {e}")
        
        finally:
            await browser.close()
    
    return matches

async def scrape_all_h2h_ligue1(confrontos, debug=False):
    """
    Busca histórico de todos os confrontos da lista
    confrontos: lista de tuplas (time1, time2)
    """
    all_h2h = {}
    
    for team1, team2 in confrontos:
        key = f"{team1} vs {team2}"
        matches = await scrape_h2h_ogol_ligue1(team1, team2, debug=debug)
        all_h2h[key] = matches
        await asyncio.sleep(2)
    
    return all_h2h

if __name__ == "__main__":
    # Teste com alguns confrontos
    confrontos_teste = [
        ("Olympique de Marselha", "Lyon"),
        ("Lille", "Monaco"),
        ("Lens", "Rennes")
    ]
    
    print("=== TESTE DO SCRAPER OGOL LIGUE 1 H2H ===\n")
    
    async def main():
        data = await scrape_all_h2h_ligue1(confrontos_teste, debug=True)
        
        print("\n=== RESULTADOS H2H ===\n")
        for confronto, matches in data.items():
            print(f"\n{confronto}: {len(matches)} jogos")
            for match in matches[:5]:  # Mostrar apenas os 5 mais recentes
                print(f"  {match['resultado']} {match['data']} {match['mandante']} {match['placar']} {match['visitante']}")
    
    asyncio.run(main())
