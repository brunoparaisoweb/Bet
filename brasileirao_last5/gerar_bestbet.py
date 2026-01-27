#!/usr/bin/env python3
"""
Gera página consolidada BestBet com as melhores apostas de todos os campeonatos
"""
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from sofascore_team_ids import get_team_logo_html

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
            # Formato: "28/01 20:30 - CAM x PAL" ou "28/01 - CAM x PAL"
            if ' - ' in texto:
                partes_antes = texto.split(' - ', 1)
                data_hora = partes_antes[0].strip()
                confronto_abrev = partes_antes[1].strip()
                
                # Extrai data e hora
                match = re.match(r'(\d{2}/\d{2})\s*(\d{1,2}:\d{2})?', data_hora)
                if match:
                    data = match.group(1)
                    hora = match.group(2) if match.group(2) else None
                else:
                    data = data_hora.split()[0] if data_hora else data_hora
                    hora = None
                
                # Expande abreviações
                times_abrev = confronto_abrev.split(' x ')
                if len(times_abrev) == 2:
                    time1_abrev = times_abrev[0].strip()
                    time2_abrev = times_abrev[1].strip()
                    time1_completo = abreviacoes_br.get(time1_abrev, time1_abrev)
                    time2_completo = abreviacoes_br.get(time2_abrev, time2_abrev)
                    confronto_completo = f"{time1_completo} x {time2_completo}"
                    
                    # Armazena data e hora juntas
                    info_jogo = {'data': data.strip()}
                    if hora:
                        info_jogo['hora'] = hora
                    jogos_rodada[confronto_completo.lower()] = info_jogo
        
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
                            
                            for jogo_key, info_jogo in jogos_rodada.items():
                                times_jogo = jogo_key.split(' x ')
                                if len(times_jogo) == 2:
                                    time1_jogo = times_jogo[0].strip()
                                    time2_jogo = times_jogo[1].strip()
                                    
                                    # Verifica se os times correspondem (em qualquer ordem)
                                    if ((time1_bet == time1_jogo and time2_bet == time2_jogo) or
                                        (time1_bet == time2_jogo and time2_bet == time1_jogo)):
                                        # info_jogo agora é um dict com 'data' e opcionalmente 'hora'
                                        data = info_jogo
                                        break
                        
                        # Formata data e hora para exibição
                        if isinstance(data, dict):
                            data_display = data.get('data', 'A definir')
                            if data.get('hora'):
                                data_display = f"{data_display} {data['hora']}"
                        elif data:
                            data_display = data
                        else:
                            data_display = 'A definir'
                        
                        bets.append({
                            'time': time_recomendado,
                            'confronto': confronto,
                            'diferenca': diferenca,
                            'data': data_display
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
            'Olympique de.': 'Olympique de Marselha',
            'OLY': 'Olympique de Marselha',
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
            # Formato: "24/01 20:30 - Team x Team" ou "24/01 - Team x Team"
            if ' - ' in texto:
                partes_antes = texto.split(' - ', 1)
                data_hora = partes_antes[0].strip()
                confronto = partes_antes[1].strip()
                confronto_original = confronto
                
                # Extrai data e hora
                match = re.match(r'(\d{2}/\d{2})\s*(\d{1,2}:\d{2})?', data_hora)
                if match:
                    data = match.group(1)
                    hora = match.group(2) if match.group(2) else None
                else:
                    data = data_hora.split()[0] if data_hora else data_hora
                    hora = None
                
                # Expande nomes abreviados no confronto da rodada
                confronto_expandido = confronto_original
                
                # Trata casos especiais de MAN (pode ser Manchester City ou Manchester United)
                if 'Arsenal x MAN' in confronto_expandido or 'MAN x Arsenal' in confronto_expandido:
                    confronto_expandido = confronto_expandido.replace('MAN', 'Manchester United')
                elif 'MAN' in confronto_expandido:
                    confronto_expandido = confronto_expandido.replace('MAN', 'Manchester City')
                
                for abrev, completo in expansoes.items():
                    confronto_expandido = confronto_expandido.replace(abrev, completo)
                
                # Armazena data e hora juntas
                info_jogo = {'data': data.strip()}
                if hora:
                    info_jogo['hora'] = hora
                jogos_rodada[confronto_expandido.lower()] = info_jogo
        
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
                    for jogo_key, info_jogo in jogos_rodada.items():
                        # Separa os times do jogo
                        times_jogo = jogo_key.split(' x ')
                        if len(times_jogo) == 2:
                            time1_jogo = times_jogo[0].strip()
                            time2_jogo = times_jogo[1].strip()
                            
                            # Verifica se os times correspondem (ordem direta ou inversa)
                            if ((time1_bet == time1_jogo and time2_bet == time2_jogo) or
                                (time1_bet == time2_jogo and time2_bet == time1_jogo)):
                                # info_jogo agora é um dict com 'data' e opcionalmente 'hora'
                                data = info_jogo
                                break
                
                # Formata data e hora para exibição
                if isinstance(data, dict):
                    data_display = data.get('data', 'A definir')
                    if data.get('hora'):
                        data_display = f"{data_display} {data['hora']}"
                elif data:
                    data_display = data
                else:
                    data_display = 'A definir'
                
                bets.append({
                    'time': time_text,
                    'confronto': confronto_text,
                    'diferenca': diferenca,
                    'data': data_display
                })
        
        return bets
    except Exception as e:
        print(f"Erro ao extrair BETs de {campeonato}: {e}")
        return []

def eh_classico(time1, time2, campeonato):
    """Verifica se o confronto é um clássico"""
    # Normaliza os nomes dos times
    time1_lower = time1.lower().strip()
    time2_lower = time2.lower().strip()
    
    # Define os clássicos de cada campeonato
    classicos = {
        'premier': [
            ('liverpool', 'manchester united'),
            ('arsenal', 'tottenham'),
            ('manchester city', 'manchester united'),
            ('newcastle', 'sunderland'),
            ('everton', 'liverpool'),
            ('chelsea', 'tottenham'),
            ('arsenal', 'manchester united'),
            ('aston villa', 'birmingham'),
            ('portsmouth', 'southampton'),
            ('leeds', 'manchester united'),
            ('arsenal', 'chelsea'),
        ],
        'laliga': [
            ('barcelona', 'real madrid'),
            ('real madrid', 'atlético'),
            ('atlético madrid', 'real madrid'),
            ('sevilla', 'real betis'),
            ('betis', 'sevilla'),
            ('barcelona', 'espanyol'),
            ('athletic club', 'real sociedad'),
            ('sociedad', 'athletic'),
            ('celta', 'coruña'),
            ('deportivo', 'celta'),
            ('valencia', 'levante'),
        ],
        'seria': [
            ('juventus', 'internazionale'),
            ('inter', 'juventus'),
            ('milan', 'inter'),
            ('inter', 'milan'),
            ('roma', 'lazio'),
            ('lazio', 'roma'),
            ('juventus', 'torino'),
            ('torino', 'juventus'),
            ('genoa', 'sampdoria'),
            ('sampdoria', 'genoa'),
            ('milan', 'juventus'),
        ],
        'ligue1': [
            ('psg', 'marseille'),
            ('paris', 'marseille'),
            ('paris saint-germain', 'marseille'),
            ('lyon', 'étienne'),
            ('lyon', 'etienne'),
            ('saint-étienne', 'lyon'),
            ('saint-etienne', 'lyon'),
            ('lyon', 'marseille'),
            ('lille', 'lens'),
            ('lens', 'lille'),
            ('monaco', 'nice'),
            ('nice', 'monaco'),
        ],
        'brasileirao': [
            ('flamengo', 'fluminense'),
            ('fluminense', 'flamengo'),
            ('palmeiras', 'corinthians'),
            ('corinthians', 'palmeiras'),
            ('grêmio', 'internacional'),
            ('gremio', 'internacional'),
            ('internacional', 'grêmio'),
            ('internacional', 'gremio'),
            ('vasco', 'flamengo'),
            ('flamengo', 'vasco'),
            ('bahia', 'vitória'),
            ('bahia', 'vitoria'),
            ('vitória', 'bahia'),
            ('vitoria', 'bahia'),
            ('athletico', 'coritiba'),
            ('athletico-pr', 'coritiba'),
            ('coritiba', 'athletico'),
            ('cruzeiro', 'atlético'),
            ('cruzeiro', 'atletico'),
            ('atlético', 'cruzeiro'),
            ('atlético-mg', 'cruzeiro'),
            ('atletico-mg', 'cruzeiro'),
            ('santos', 'são paulo'),
            ('santos', 'sao paulo'),
            ('são paulo', 'santos'),
            ('sao paulo', 'santos'),
            ('flamengo', 'palmeiras'),
            ('palmeiras', 'flamengo'),
            ('flamengo', 'botafogo'),
            ('botafogo', 'flamengo'),
            ('corinthians', 'são paulo'),
            ('corinthians', 'sao paulo'),
            ('são paulo', 'corinthians'),
            ('sao paulo', 'corinthians'),
            ('corinthians', 'santos'),
            ('santos', 'corinthians'),
            ('palmeiras', 'santos'),
            ('santos', 'palmeiras'),
        ]
    }
    
    # Obtém a lista de clássicos do campeonato
    classicos_campeonato = classicos.get(campeonato, [])
    
    # Verifica se o confronto está na lista de clássicos (em qualquer ordem)
    for time_a, time_b in classicos_campeonato:
        if ((time_a in time1_lower or time1_lower in time_a) and (time_b in time2_lower or time2_lower in time_b)) or \
           ((time_a in time2_lower or time2_lower in time_a) and (time_b in time1_lower or time1_lower in time_b)):
            return True
    
    return False

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
    def gerar_secao(titulo, cor, bets, arquivo_html, campeonato_id, script_python, usar_delta=False):
        cor_texto = 'color: #000;' if cor == '#87CEEB' else ''
        data_modificacao = obter_data_modificacao(arquivo_html)
        info_data = f'<span class="info-data" id="data-{campeonato_id}">Atualizado: {data_modificacao}</span>' if data_modificacao else ''
        
        html = f'''        <div class="campeonato-section">
            <div class="campeonato-header" style="background: {cor}; {cor_texto}">
                <div class="header-content">
                    <span>{titulo}</span>
                    {info_data}
                </div>
                <div class="header-actions">
                    <button class="update-btn" onclick="atualizarCampeonato('{campeonato_id}')" title="Atualizar análise">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="23 4 23 10 17 10"></polyline>
                            <polyline points="1 20 1 14 7 14"></polyline>
                            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                        </svg>
                    </button>
                    <a href="{arquivo_html}" target="_blank" class="detail-link" title="Ver análise completa">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="16" x2="12" y2="12"></line>
                            <line x1="12" y1="8" x2="12.01" y2="8"></line>
                        </svg>
                    </a>
                </div>
            </div>
            <div class="progress-container" id="progress-{campeonato_id}" style="display: none;">
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill-{campeonato_id}"></div>
                </div>
                <div class="progress-text" id="progress-text-{campeonato_id}">Iniciando...</div>
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
                    
                    # Verifica se é um clássico
                    is_classico = eh_classico(time1, time2, campeonato_id)
                    class_classico = ' classico' if is_classico else ''
                    badge_classico = '<div class="classico-badge">⭐ Clássico</div>\n                    ' if is_classico else ''
                    
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
                    
                    # Adiciona escudos dos times
                    logo1 = get_team_logo_html(time1, "24px")
                    logo2 = get_team_logo_html(time2, "24px")
                    
                    html += f'''                <div class="bet-card{class_classico}" style="border-top: 4px solid {cor};">
                    {badge_classico}<div class="bet-data">{bet.get('data', 'A definir')}</div>
                    <div class="bet-card-content">
                        <div class="time-linha">{logo1}{time1_html}</div>
                        <div class="versus">x</div>
                        <div class="time-linha">{logo2}{time2_html}</div>
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
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .server-info {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 5px;
        }
        .server-status {
            font-size: 0.8em;
            color: #666;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #4CAF50;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .restart-btn {
            background: linear-gradient(135deg, #f44336 0%, #e91e63 100%);
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(244, 67, 54, 0.3);
        }
        .restart-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(244, 67, 54, 0.5);
        }
        .restart-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .restart-btn svg {
            width: 20px;
            height: 20px;
        }
        .publish-btn {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3);
        }
        .publish-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(76, 175, 80, 0.5);
        }
        .publish-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .publish-btn svg {
            width: 20px;
            height: 20px;
        }
        .selection-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 15px;
            padding: 12px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .selection-btn {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: #fff;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.85em;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.3s;
        }
        .selection-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3);
        }
        .selection-counter {
            font-size: 0.9em;
            color: #666;
            font-weight: bold;
            padding: 8px 12px;
            background: #fff;
            border-radius: 6px;
            border: 2px solid #2196F3;
            margin-left: auto;
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
            position: relative;
        }
        .bet-card.selected {
            background: #e3f2fd;
            box-shadow: 0 0 0 3px #2196F3;
            transform: scale(1.02);
        }
        .bet-checkbox {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 24px;
            height: 24px;
            cursor: pointer;
            z-index: 10;
            accent-color: #2196F3;
        }
        .bet-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .bet-card.classico {
            background: linear-gradient(135deg, #fff8dc 0%, #fffaed 100%);
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
            border: 2px solid #FFD700;
            border-top: 4px solid #FFD700 !important;
            padding-top: 18px;
        }
        .bet-card.classico:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6);
        }
        .classico-badge {
            position: absolute;
            top: 2px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.6em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.5);
            border: 1px solid #FFD700;
            z-index: 10;
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
        .header-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header-actions {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .info-data {
            font-size: 0.75em;
            opacity: 0.9;
        }
        .update-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #fff;
            cursor: pointer;
            padding: 5px 8px;
            border-radius: 5px;
            display: inline-flex;
            align-items: center;
            transition: all 0.2s;
        }
        .update-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.1);
        }
        .update-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .progress-container {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            width: 0%;
        }
        .progress-text {
            text-align: center;
            font-size: 0.85em;
            color: #666;
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
        <div class="header-container">
            <h1>🏆 BestBet 🏆</h1>
            <div class="server-info">
                <div class="server-status">
                    <span class="status-indicator"></span>
                    <span id="server-time">Carregando...</span>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button class="publish-btn" onclick="publicarBets()" title="Publicar Bets no App">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="17 8 12 3 7 8"/>
                            <line x1="12" y1="3" x2="12" y2="15"/>
                        </svg>
                        Publicar no App
                    </button>
                    <button class="restart-btn" onclick="reiniciarServidor()" title="Reiniciar Servidor">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                        </svg>
                        Reiniciar Servidor
                    </button>
                </div>
            </div>
        </div>

        <!-- Controles de Seleção -->
        <div class="selection-controls">
            <button class="selection-btn" onclick="selecionarTodas()" title="Selecionar todas as bets">
                ✓ Selecionar Todas
            </button>
            <button class="selection-btn" onclick="deselecionarTodas()" title="Desselecionar todas as bets">
                ✗ Desselecionar Todas
            </button>
            <span class="selection-counter" id="selection-counter">
                📊 Selecionadas: <strong>0</strong> / <strong id="total-bets">0</strong>
            </span>
        </div>
        
'''
    
    # Adiciona cada seção
    html += gerar_secao('⚽ Brasileirão Betano', '#87CEEB', bets_brasileirao, 'sofascore_result.html', 'brasileirao', 'sofascore_to_html.py', usar_delta=True)
    html += gerar_secao('🇪🇸 Campeonato Espanhol (La Liga)', '#FF4C00', bets_laliga, 'laliga_analysis.html', 'laliga', 'gerar_html_laliga.py')
    html += gerar_secao('🇮🇹 Campeonato Italiano (Serie A)', '#0082c8', bets_seria, 'seria_analysis.html', 'seria', 'gerar_html_seria.py')
    html += gerar_secao('🇫🇷 Campeonato Francês (Ligue 1)', '#003DA5', bets_ligue1, 'LIGUE1_analysis.html', 'ligue1', 'gerar_html_ligue1.py')
    html += gerar_secao('🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League', '#37003c', bets_premier, 'premier_league_analysis.html', 'premier', 'gerar_html_pl.py')
    
    # JavaScript para atualização
    html += '''    </div>
    
    <script>
        const API_URL = 'http://localhost:5000';
        const BACKEND_API_URL = 'http://localhost:3000'; // Backend BetApp
        
        // Inicialização ao carregar a página
        window.addEventListener('DOMContentLoaded', () => {
            adicionarCheckboxes();
            atualizarContador();
            carregarInfoServidor();
        });
        
        // Adiciona checkboxes em todas as bet-cards
        function adicionarCheckboxes() {
            const betCards = document.querySelectorAll('.bet-card');
            betCards.forEach(card => {
                // Verifica se já tem checkbox
                if (!card.querySelector('.bet-checkbox')) {
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.className = 'bet-checkbox';
                    checkbox.checked = true; // Todas selecionadas por padrão
                    checkbox.onchange = atualizarContador;
                    
                    // Adiciona evento de clique no card para marcar/desmarcar
                    card.addEventListener('click', (e) => {
                        if (e.target !== checkbox) {
                            checkbox.checked = !checkbox.checked;
                            card.classList.toggle('selected', checkbox.checked);
                            atualizarContador();
                        }
                    });
                    
                    // Adiciona o checkbox no início do card
                    card.insertBefore(checkbox, card.firstChild);
                    
                    // Adiciona classe selected se estiver marcado
                    if (checkbox.checked) {
                        card.classList.add('selected');
                    }
                }
            });
        }
        
        // Atualiza contador de bets selecionadas
        function atualizarContador() {
            const checkboxes = document.querySelectorAll('.bet-checkbox');
            const total = checkboxes.length;
            const selecionadas = Array.from(checkboxes).filter(cb => cb.checked).length;
            
            const counter = document.getElementById('selection-counter');
            const totalElement = document.getElementById('total-bets');
            
            if (counter && totalElement) {
                counter.innerHTML = `📊 Selecionadas: <strong>${selecionadas}</strong> / <strong id="total-bets">${total}</strong>`;
                
                // Atualiza classes selected nos cards
                checkboxes.forEach(checkbox => {
                    const card = checkbox.closest('.bet-card');
                    if (card) {
                        card.classList.toggle('selected', checkbox.checked);
                    }
                });
            }
        }
        
        // Seleciona todas as bets
        function selecionarTodas() {
            const checkboxes = document.querySelectorAll('.bet-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
            atualizarContador();
        }
        
        // Desseleciona todas as bets
        function deselecionarTodas() {
            const checkboxes = document.querySelectorAll('.bet-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            atualizarContador();
        }
        
        // Função para extrair bets da página (MODIFICADA para filtrar selecionadas)
        function extrairBetsDaPagina() {
            const bets = [];
            const leagues = [];
            
            // Seleciona todas as seções de campeonatos
            const campeonatoSections = document.querySelectorAll('.campeonato-section');
            
            campeonatoSections.forEach(section => {
                const header = section.querySelector('.campeonato-header .header-content');
                const leagueName = header ? header.textContent.trim() : '';
                
                if (leagueName && !leagues.includes(leagueName)) {
                    leagues.push(leagueName);
                }
                
                // Extrai bets de cada seção
                const betCards = section.querySelectorAll('.bet-card');
                betCards.forEach(card => {
                    // Verifica se a bet está selecionada
                    const checkbox = card.querySelector('.bet-checkbox');
                    if (!checkbox || !checkbox.checked) {
                        return; // Pula bets não selecionadas
                    }
                    
                    // Extrai data
                    const dataElement = card.querySelector('.bet-data');
                    const dataHora = dataElement ? dataElement.textContent.trim() : 'A definir';
                    
                    // Separa data e hora
                    let data = '';
                    let hora = '';
                    if (dataHora && dataHora !== 'A definir') {
                        const partes = dataHora.split(' ');
                        data = partes[0] || '';
                        hora = partes[1] || '';
                    }
                    
                    // Extrai times e escudos
                    const timesElements = card.querySelectorAll('.time-linha');
                    const times = [];
                    const badges = [];
                    let timeRecomendado = '';
                    
                    timesElements.forEach(timeLinha => {
                        const img = timeLinha.querySelector('img');
                        const timeDestaque = timeLinha.querySelector('.time-destaque');
                        
                        // Pega o nome do time
                        let timeText = '';
                        if (timeDestaque) {
                            timeText = timeDestaque.textContent.trim();
                            timeRecomendado = timeText;
                        } else if (img) {
                            timeText = img.alt || '';
                        }
                        
                        times.push(timeText);
                        badges.push(img ? img.src : '');
                    });
                    
                    // Monta o confronto
                    const match = times.join(' x ');
                    
                    // Cria objeto da bet
                    bets.push({
                        league: leagueName,
                        match: match,
                        date: data,
                        time: hora,
                        dateTime: dataHora,
                        homeTeam: times[0] || '',
                        awayTeam: times[1] || '',
                        homeBadge: badges[0] || '',
                        awayBadge: badges[1] || '',
                        bet: timeRecomendado,
                        recommendation: timeRecomendado,
                        difference: 0,
                        delta: 0
                    });
                });
            });
            
            return { bets, leagues };
        }
        
        // Função para publicar bets no backend
        async function publicarBets() {
            const btn = document.querySelector('.publish-btn');
            
            // Conta quantas bets estão selecionadas
            const checkboxes = document.querySelectorAll('.bet-checkbox:checked');
            const totalSelecionadas = checkboxes.length;
            
            if (totalSelecionadas === 0) {
                alert('⚠️ Nenhuma bet selecionada!\\n\\nSelecione pelo menos uma bet para publicar.');
                return;
            }
            
            if (!confirm(`📤 Publicar ${totalSelecionadas} bet(s) selecionada(s) no aplicativo móvel?`)) {
                return;
            }
            
            btn.disabled = true;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> Publicando...';
            
            try {
                // Extrai bets da página (apenas selecionadas)
                const { bets, leagues } = extrairBetsDaPagina();
                
                if (bets.length === 0) {
                    alert('Nenhuma bet encontrada para publicar!');
                    btn.disabled = false;
                    btn.innerHTML = originalHTML;
                    return;
                }
                
                // Envia para o backend
                const response = await fetch(`${BACKEND_API_URL}/api/bets/publish`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        bets: bets,
                        leagues: leagues,
                        generatedAt: new Date().toISOString()
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Publicado!';
                    alert(`✅ ${bets.length} bets publicadas com sucesso!\\n\\nAs bets já estão disponíveis no aplicativo móvel.`);
                    
                    setTimeout(() => {
                        btn.innerHTML = originalHTML;
                        btn.disabled = false;
                    }, 3000);
                } else {
                    throw new Error(data.error || 'Erro ao publicar');
                }
            } catch (error) {
                console.error('Erro ao publicar:', error);
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg> Erro!';
                alert(`❌ Erro ao publicar bets:\\n\\n${error.message}\\n\\nVerifique se o servidor backend está rodando na porta 3000.`);
                btn.disabled = false;
                
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                }, 3000);
            }
        }
        
        // Carrega informações do servidor
        async function carregarInfoServidor() {
            try {
                const response = await fetch(`${API_URL}/server_info`);
                const data = await response.json();
                
                if (data.data_inicio) {
                    document.getElementById('server-time').textContent = `Servidor iniciado: ${data.data_inicio}`;
                }
            } catch (error) {
                console.error('Erro ao carregar info do servidor:', error);
                document.getElementById('server-time').textContent = 'Servidor offline';
            }
        }
        
        async function atualizarCampeonato(campeonato) {
            const progressContainer = document.getElementById(`progress-${campeonato}`);
            const progressFill = document.getElementById(`progress-fill-${campeonato}`);
            const progressText = document.getElementById(`progress-text-${campeonato}`);
            const updateBtn = document.querySelector(`button[onclick="atualizarCampeonato('${campeonato}')"]`);
            
            // Mostra barra de progresso
            progressContainer.style.display = 'block';
            updateBtn.disabled = true;
            
            try {
                // Inicia atualização
                const response = await fetch(`${API_URL}/atualizar/${campeonato}`, {
                    method: 'POST'
                });
                
                if (!response.ok) {
                    throw new Error('Erro ao iniciar atualização');
                }
                
                // Monitora progresso
                const checkProgress = setInterval(async () => {
                    const progressResponse = await fetch(`${API_URL}/progresso/${campeonato}`);
                    const data = await progressResponse.json();
                    
                    progressFill.style.width = `${data.progresso}%`;
                    progressText.textContent = data.mensagem;
                    
                    if (data.status === 'success') {
                        clearInterval(checkProgress);
                        progressText.textContent = 'Concluído! Recarregando página...';
                        
                        // Atualiza a data de modificação
                        if (data.data_modificacao) {
                            const dataElement = document.getElementById(`data-${campeonato}`);
                            if (dataElement) {
                                dataElement.textContent = `Atualizado: ${data.data_modificacao}`;
                            }
                        }
                        
                        // Recarrega a página após 2 segundos
                        setTimeout(() => {
                            location.reload();
                        }, 2000);
                    } else if (data.status === 'error') {
                        clearInterval(checkProgress);
                        progressFill.style.background = '#f44336';
                        updateBtn.disabled = false;
                        
                        setTimeout(() => {
                            progressContainer.style.display = 'none';
                            progressFill.style.width = '0%';
                            progressFill.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
                        }, 3000);
                    }
                }, 500);
                
            } catch (error) {
                console.error('Erro:', error);
                progressText.textContent = 'Erro ao atualizar. Verifique se o servidor está rodando.';
                progressFill.style.background = '#f44336';
                updateBtn.disabled = false;
                
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressFill.style.width = '0%';
                    progressFill.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
                }, 3000);
            }
        }
        
        async function reiniciarServidor() {
            const btn = document.querySelector('.restart-btn');
            
            if (!confirm('Tem certeza que deseja reiniciar o servidor?')) {
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg> Reiniciando...';
            
            try {
                const response = await fetch(`${API_URL}/restart`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg> Servidor Reiniciado!';
                    
                    // Aguarda 3 segundos e recarrega a página
                    setTimeout(() => {
                        location.reload();
                    }, 3000);
                } else {
                    throw new Error('Erro ao reiniciar servidor');
                }
            } catch (error) {
                console.error('Erro:', error);
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg> Erro ao Reiniciar';
                btn.disabled = false;
                
                setTimeout(() => {
                    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg> Reiniciar Servidor';
                }, 3000);
            }
        }
    </script>
    
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
