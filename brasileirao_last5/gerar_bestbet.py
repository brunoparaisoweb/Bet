#!/usr/bin/env python3
"""
Gera página consolidada BestBet com as melhores apostas de todos os campeonatos
"""
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

def extrair_bets_brasileirao(html_path):
    """Extrai BETs do Brasileirão"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Mapeamento de abreviações para nomes completos do Brasileirão
        abreviacoes_br = {
            'CAM': 'Atlético-MG', 'PAL': 'Palmeiras', 'INT': 'Internacional',
            'CAP': 'Athletico-PR', 'CFC': 'Coritiba', 'RBB': 'RB Bragantino',
            'VIT': 'Vitória', 'REM': 'Remo', 'FLU': 'Fluminense',
            'GRE': 'Grêmio', 'COR': 'Corinthians', 'BAH': 'Bahia',
            'CHA': 'Chapecoense', 'SAN': 'Santos', 'SAO': 'São Paulo',
            'FLA': 'Flamengo', 'MIR': 'Mirassol', 'VAS': 'Vasco',
            'BOT': 'Botafogo', 'CRU': 'Cruzeiro', 'FOR': 'Fortaleza',
            'ATL': 'Atlético-MG', 'JUV': 'Juventude', 'CEA': 'Ceará',
            'SPO': 'Sport', 'ATM': 'Atlético-MG'
        }
        
        # Extrai jogos da próxima rodada para obter datas
        jogos_rodada = {}
        jogos_divs = soup.find_all('div', class_='jogo-rodada')
        for jogo_div in jogos_divs:
            texto = jogo_div.get_text(strip=True)
            # Formato: "28/01 - CAM x PAL"
            if ' - ' in texto:
                data, confronto_abrev = texto.split(' - ', 1)
                # Expande abreviações
                times_abrev = confronto_abrev.split(' x ')
                if len(times_abrev) == 2:
                    time1_abrev = times_abrev[0].strip()
                    time2_abrev = times_abrev[1].strip()
                    time1_completo = abreviacoes_br.get(time1_abrev, time1_abrev)
                    time2_completo = abreviacoes_br.get(time2_abrev, time2_abrev)
                    confronto_completo = f"{time1_completo} x {time2_completo}"
                    jogos_rodada[confronto_completo.lower()] = data.strip()
        
        bets = []
        bets_table = soup.find('table', class_='bets-table')
        if bets_table:
            rows = bets_table.find_all('tr')[1:]
            for row in rows:
                td = row.find('td')
                if td:
                    text = td.get_text(strip=True)
                    bet_time = row.find('span', class_='bet-time')
                    if bet_time:
                        time_recomendado = bet_time.get_text(strip=True)
                        lines = text.split('\n')
                        # Pega apenas a primeira linha que contém o confronto (ex: "Mirassol vs Vasco")
                        confronto_raw = lines[0] if lines else text.split('Créditos:')[0].strip()
                        # Remove "Créditos:" e tudo após
                        confronto = confronto_raw.split('Créditos:')[0].strip()
                        # Extrai a diferença
                        diff_match = re.search(r'Δ\s*([\d.]+)', text)
                        diferenca = diff_match.group(1) if diff_match else '0'
                        
                        # Busca a data correspondente
                        data = None
                        # Normaliza o confronto (vs -> x, remove espaços extras)
                        confronto_normalizado = confronto.lower()
                        confronto_normalizado = re.sub(r'\s*vs\.?\s*', ' x ', confronto_normalizado)
                        confronto_normalizado = re.sub(r'\s+', ' ', confronto_normalizado).strip()
                        
                        # Extrai os times do confronto normalizado
                        times_confronto = confronto_normalizado.split(' x ')
                        if len(times_confronto) == 2:
                            time1_bet = times_confronto[0].strip()
                            time2_bet = times_confronto[1].strip()
                            
                            for jogo_key, jogo_data in jogos_rodada.items():
                                times_jogo = jogo_key.split(' x ')
                                if len(times_jogo) == 2:
                                    time1_jogo = times_jogo[0].strip()
                                    time2_jogo = times_jogo[1].strip()
                                    
                                    # Verifica se os times correspondem (em qualquer ordem)
                                    if ((time1_bet == time1_jogo and time2_bet == time2_jogo) or
                                        (time1_bet == time2_jogo and time2_bet == time1_jogo)):
                                        data = jogo_data
                                        break
                        
                        bets.append({
                            'time': time_recomendado,
                            'confronto': confronto,
                            'diferenca': diferenca,
                            'data': data or 'A definir'
                        })
        return bets
    except Exception as e:
        print(f"Erro ao extrair BETs do Brasileirão: {e}")
        return []

def extrair_bets_padrao(html_path, campeonato):
    """Extrai BETs dos campeonatos com formato padrão"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Dicionário de expansão de nomes abreviados
        expansoes = {
            'Crystal Pala.': 'Crystal Palace',
            'Manchester C.': 'Manchester City',
            'Manchester U.': 'Manchester United',
            'Wolverhampto.': 'Wolverhampton',
            'Atl. Madrid': 'Atlético Madrid',
            'Atlético Mad.': 'Atlético Madrid',
            'Athletic Clu.': 'Athletic Club',
            'Real Socieda.': 'Real Sociedad',
            'Internaziona.': 'Internazionale',
            'Paris Saint-.': 'Paris Saint-Germain',
            'Saint-Étienn.': 'Saint-Étienne',
            'WOL': 'Wolverhampton',
            'BOU': 'Bournemouth',
            'NOT': 'Nottingham Forest',
            'CRY': 'Crystal Palace',
            'AST': 'Aston Villa',
            'LEE': 'Leeds United',
            'INT': 'Internazionale',
            'HEL': 'Hellas Verona',
            'PAR': 'Paris Saint-Germain'
        }
        
        # Extrai jogos da próxima rodada para obter datas
        jogos_rodada = {}
        jogos_divs = soup.find_all('div', class_='jogo-rodada')
        for jogo_div in jogos_divs:
            texto = jogo_div.get_text(strip=True)
            # Formato: "24/01 - Team x Team"
            if ' - ' in texto:
                data, confronto = texto.split(' - ', 1)
                confronto_original = confronto.strip()
                
                # Expande nomes abreviados no confronto da rodada
                confronto_expandido = confronto_original
                
                # Trata casos especiais de MAN (pode ser Manchester City ou Manchester United)
                if 'Arsenal x MAN' in confronto_expandido or 'MAN x Arsenal' in confronto_expandido:
                    confronto_expandido = confronto_expandido.replace('MAN', 'Manchester United')
                elif 'MAN' in confronto_expandido:
                    confronto_expandido = confronto_expandido.replace('MAN', 'Manchester City')
                
                for abrev, completo in expansoes.items():
                    confronto_expandido = confronto_expandido.replace(abrev, completo)
                
                jogos_rodada[confronto_expandido.lower()] = data.strip()
        
        bets = []
        bet_items = soup.find_all('div', class_='bet-item')
        
        for item in bet_items:
            time = item.find('div', class_='bet-time')
            matchup = item.find('div', class_='bet-matchup')
            diff = item.find('div', class_='bet-diff')
            
            if time and matchup and diff:
                time_text = time.get_text(strip=True)
                confronto_text = matchup.get_text(strip=True)
                diff_text = diff.get_text(strip=True)
                
                # Expande nomes abreviados
                for abrev, completo in expansoes.items():
                    confronto_text = confronto_text.replace(abrev, completo)
                
                diff_match = re.search(r'([\d.]+)', diff_text)
                diferenca = diff_match.group(1) if diff_match else '0'
                
                # Busca a data correspondente
                data = None
                # Normaliza o confronto da BET (substitui vs por x)
                confronto_normalizado = confronto_text.lower()
                confronto_normalizado = re.sub(r'\s*vs\.?\s*', ' x ', confronto_normalizado)
                confronto_normalizado = re.sub(r'\s+', ' ', confronto_normalizado).strip()
                
                # Separa os times do confronto da BET
                times_bet = confronto_normalizado.split(' x ')
                if len(times_bet) == 2:
                    time1_bet = times_bet[0].strip()
                    time2_bet = times_bet[1].strip()
                    
                    # Busca correspondência nos jogos da rodada
                    for jogo_key, jogo_data in jogos_rodada.items():
                        # Separa os times do jogo
                        times_jogo = jogo_key.split(' x ')
                        if len(times_jogo) == 2:
                            time1_jogo = times_jogo[0].strip()
                            time2_jogo = times_jogo[1].strip()
                            
                            # Verifica se os times correspondem (ordem direta ou inversa)
                            if ((time1_bet == time1_jogo and time2_bet == time2_jogo) or
                                (time1_bet == time2_jogo and time2_bet == time1_jogo)):
                                data = jogo_data
                                break
                
                bets.append({
                    'time': time_text,
                    'confronto': confronto_text,
                    'diferenca': diferenca,
                    'data': data or 'A definir'
                })
        
        return bets
    except Exception as e:
        print(f"Erro ao extrair BETs de {campeonato}: {e}")
        return []

def gerar_html_bestbet():
    """Gera o HTML consolidado BestBet"""
    
    # Extrair BETs de cada campeonato
    print("Extraindo BETs do Brasileirão...")
    bets_brasileirao = extrair_bets_brasileirao('sofascore_result.html')
    
    print("Extraindo BETs da La Liga...")
    bets_laliga = extrair_bets_padrao('laliga_analysis.html', 'La Liga')
    
    print("Extraindo BETs da Serie A...")
    bets_seria = extrair_bets_padrao('seria_analysis.html', 'Serie A')
    
    print("Extraindo BETs da Ligue 1...")
    bets_ligue1 = extrair_bets_padrao('LIGUE1_analysis.html', 'Ligue 1')
    
    print("Extraindo BETs da Premier League...")
    bets_premier = extrair_bets_padrao('premier_league_analysis.html', 'Premier League')
    
    # Função para obter data de modificação do arquivo
    def obter_data_modificacao(arquivo):
        try:
            timestamp = os.path.getmtime(arquivo)
            data_hora = datetime.fromtimestamp(timestamp)
            return data_hora.strftime('%d/%m/%Y %H:%M')
        except:
            return ''
    
    # Gera seções HTML
    def gerar_secao(titulo, cor, bets, arquivo_html, usar_delta=False):
        cor_texto = 'color: #000;' if cor == '#87CEEB' else ''
        data_modificacao = obter_data_modificacao(arquivo_html)
        info_data = f'<span style="font-size: 0.75em; opacity: 0.9; margin-left: 10px;">Atualizado: {data_modificacao}</span>' if data_modificacao else ''
        
        html = f'''        <div class="campeonato-section">
            <div class="campeonato-header" style="background: {cor}; {cor_texto}">
                <div>
                    {titulo}
                    {info_data}
                </div>
                <a href="{arquivo_html}" target="_blank" class="detail-link" title="Ver análise completa">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                </a>
            </div>
            <div class="bet-grid">
'''
        
        if bets:
            for bet in bets:
                # Adiciona espaços ao redor de 'vs', 'x', 'vs.', etc
                confronto_formatado = bet['confronto']
                confronto_formatado = confronto_formatado.replace('vs', ' x ')
                confronto_formatado = confronto_formatado.replace('vs.', ' x ')
                confronto_formatado = re.sub(r'\s+', ' ', confronto_formatado).strip()
                
                # Destaca o time recomendado
                time_recomendado = bet['time']
                
                # Separa os times do confronto
                times_confronto = confronto_formatado.split(' x ')
                if len(times_confronto) == 2:
                    time1 = times_confronto[0].strip()
                    time2 = times_confronto[1].strip()
                    
                    # Verifica qual time deve ser destacado usando matching parcial
                    time_destacado = None
                    time1_destacado = False
                    time2_destacado = False
                    
                    # Tenta match direto primeiro
                    if time_recomendado == time1 or time_recomendado == time2:
                        time_destacado = time_recomendado
                        time1_destacado = (time_recomendado == time1)
                        time2_destacado = (time_recomendado == time2)
                    # Tenta match parcial (time recomendado contém parte do nome abreviado ou vice-versa)
                    elif time_recomendado.lower().startswith(time1.lower()[:5]) or time1.lower().startswith(time_recomendado.lower()[:5]):
                        time1_destacado = True
                    elif time_recomendado.lower().startswith(time2.lower()[:5]) or time2.lower().startswith(time_recomendado.lower()[:5]):
                        time2_destacado = True
                    # Tenta match por palavras-chave
                    else:
                        palavras_rec = time_recomendado.lower().split()
                        palavras_t1 = time1.lower().split()
                        palavras_t2 = time2.lower().split()
                        
                        # Verifica se alguma palavra significativa corresponde
                        for palavra in palavras_rec:
                            if len(palavra) >= 4:  # Ignora palavras muito curtas
                                if any(palavra in p or p in palavra for p in palavras_t1):
                                    time1_destacado = True
                                    break
                                elif any(palavra in p or p in palavra for p in palavras_t2):
                                    time2_destacado = True
                                    break
                    
                    # Aplica o destaque
                    time1_html = f'<span class="time-destaque">{time1}</span>' if time1_destacado else time1
                    time2_html = f'<span class="time-destaque">{time2}</span>' if time2_destacado else time2
                    
                    html += f'''                <div class="bet-card" style="border-top: 4px solid {cor};">
                    <div class="bet-data">{bet.get('data', 'A definir')}</div>
                    <div class="bet-card-content">
                        <div class="time-linha">{time1_html}</div>
                        <div class="versus">x</div>
                        <div class="time-linha">{time2_html}</div>
                    </div>
                </div>
'''
                else:
                    # Fallback se não conseguir separar
                    html += f'''                <div class="bet-card" style="border-top: 4px solid {cor};">
                    <div class="bet-card-content">
                        {confronto_formatado}
                    </div>
                </div>
'''
        else:
            html += '                <div class="no-bets">Nenhuma BET disponível</div>\n'
        
        html += '            </div>\n        </div>\n'
        return html
    
    # Monta HTML completo
    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BestBet - Melhores Apostas</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px 10px 30px 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #fff;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            padding: 15px;
        }
        h1 {
            text-align: center;
            color: #333;
            font-size: 2em;
            margin: 0 0 15px 0;
            text-transform: uppercase;
            letter-spacing: 3px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .campeonato-section {
            margin-bottom: 12px;
        }
        .campeonato-header {
            padding: 8px 15px;
            color: #fff;
            font-size: 0.95em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .detail-link {
            color: #fff;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            transition: transform 0.2s;
            opacity: 0.9;
        }
        .detail-link:hover {
            transform: scale(1.2);
            opacity: 1;
        }
        .detail-link svg {
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.3));
        }
        .bet-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 12px;
            margin-bottom: 5px;
        }
        .bet-card {
            background: #fff;
            padding: 10px 8px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-top: 4px solid;
            text-align: center;
        }
        .bet-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .bet-card-content {
            font-weight: bold;
            font-size: 0.75em;
            color: #333;
            margin-bottom: 0;
            line-height: 1.2;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }
        .time-linha {
            text-align: center;
            width: 100%;
            word-wrap: break-word;
            overflow-wrap: break-word;
            hyphens: auto;
        }
        .versus {
            color: #999;
            font-size: 0.85em;
            font-weight: normal;
            margin: 1px 0;
        }
        .time-destaque {
            color: #d00;
            font-weight: 900;
            font-size: 1.2em;
            text-decoration: underline;
        }
        .bet-data {
            font-size: 0.7em;
            color: #666;
            margin-bottom: 5px;
            font-weight: normal;
        }
        .no-bets {
            text-align: center;
            padding: 20px;
            color: #999;
            font-style: italic;
            grid-column: 1 / -1;
        }
        footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #333;
            color: #fff;
            text-align: center;
            padding: 8px 0;
            font-size: 11px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 BestBet 🏆</h1>
        
'''
    
    # Adiciona cada seção
    html += gerar_secao('⚽ Brasileirão Betano', '#87CEEB', bets_brasileirao, 'sofascore_result.html', usar_delta=True)
    html += gerar_secao('🇪🇸 Campeonato Espanhol (La Liga)', '#FF4C00', bets_laliga, 'laliga_analysis.html')
    html += gerar_secao('🇮🇹 Campeonato Italiano (Serie A)', '#0082c8', bets_seria, 'seria_analysis.html')
    html += gerar_secao('🇫🇷 Campeonato Francês (Ligue 1)', '#003DA5', bets_ligue1, 'LIGUE1_analysis.html')
    html += gerar_secao('🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League', '#37003c', bets_premier, 'premier_league_analysis.html')
    
    # Footer
    html += '''    </div>
    
    <footer>Development for Bruno Paraiso - 2026 | Todos os direitos reservados</footer>
</body>
</html>'''
    
    # Salva o arquivo
    with open('bestbet.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n✅ Arquivo bestbet.html gerado com sucesso!")
    print(f"   - Brasileirão: {len(bets_brasileirao)} BETs")
    print(f"   - La Liga: {len(bets_laliga)} BETs")
    print(f"   - Serie A: {len(bets_seria)} BETs")
    print(f"   - Ligue 1: {len(bets_ligue1)} BETs")
    print(f"   - Premier League: {len(bets_premier)} BETs")

if __name__ == "__main__":
    gerar_html_bestbet()
