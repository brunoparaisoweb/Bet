# -*- coding: utf-8 -*-
"""
IDs dos times no SofaScore para carregar os escudos
"""

TEAM_IDS = {
    # Brasileirão
    'Flamengo': 5981,
    'Palmeiras': 1963,
    'Corinthians': 1957,
    'São Paulo': 1981,
    'Santos': 1968,
    'Grêmio': 5926,
    'Internacional': 1966,
    'Atlético-MG': 1977,
    'Fluminense': 1961,
    'Botafogo': 1958,
    'Vasco': 1974,
    'Athletico-PR': 1967,
    'Cruzeiro': 1954,
    'Bahia': 1955,
    'Vitória': 1962,
    'Fortaleza': 5531,
    'Ceará': 10633,
    'Sport': 1974,
    'Chapecoense': 21845,
    'Coritiba': 1982,
    'Mirassol': 21982,
    'Remo': 2012,
    'Bragantino': 1999,
    'RB Bragantino': 1999,
    
    # Premier League
    'Liverpool': 44,
    'Manchester City': 17,
    'Man City': 17,
    'Manchester United': 35,
    'Man Utd': 35,
    'Arsenal': 42,
    'Chelsea': 38,
    'Tottenham': 33,
    'Newcastle': 39,
    'Aston Villa': 40,
    'Brighton': 30,
    'Brighton & Hove Albion': 30,
    'West Ham': 37,
    'Crystal Palace': 7,
    'Brentford': 50,
    'Fulham': 43,
    'Wolverhampton': 3,
    'Wolves': 3,
    'Everton': 48,
    'Leeds United': 34,
    'Leeds': 34,
    'Nottingham Forest': 14,
    'Forest': 14,
    'Bournemouth': 60,
    'Burnley': 6,
    'Sunderland': 41,
    
    # La Liga
    'Barcelona': 2817,
    'Real Madrid': 2829,
    'Atlético Madrid': 2836,
    'Atl. Madrid': 2836,
    'Atlético de Madrid': 2836,
    'Sevilla': 2833,
    'Real Betis': 2816,
    'Betis': 2816,
    'Athletic Club': 2825,
    'Athletic Bilbao': 2825,
    'Real Sociedad': 2824,
    'Valencia': 2828,
    'Villarreal': 2819,
    'Celta': 2821,
    'Celta de Vigo': 2821,
    'Espanyol': 2814,
    'Getafe': 2859,
    'Mallorca': 2826,
    'Girona': 24264,
    'Alavés': 2885,
    'Levante': 2849,
    'Real Oviedo': 2851,
    'Osasuna': 2820,
    'Rayo Vallecano': 2818,
    'Elche': 2846,
    
    # Serie A
    'Juventus': 2687,
    'Inter': 2697,
    'Internazionale': 2697,
    'Milan': 2692,
    'AC Milan': 2692,
    'Napoli': 2714,
    'Roma': 2702,
    'Lazio': 2699,
    'Atalanta': 2686,
    'Fiorentina': 2693,
    'Torino': 2696,
    'Bologna': 2685,
    'Genoa': 2713,
    'Cagliari': 2719,
    'Parma': 2690,
    'Como': 2704,
    'Como 1907': 2704,
    'Pisa': 2737,
    'Hellas Verona': 2701,
    'Verona': 2701,
    'Udinese': 2695,
    'Sassuolo': 2793,
    'Cremonese': 2761,
    'Lecce': 2689,
    
    # Ligue 1
    'Paris Saint-Germain': 1644,
    'PSG': 1644,
    'Olympique de Marselha': 1641,
    'Marseille': 1641,
    'OM': 1641,
    'OLY': 1641,
    'Olympique Marseille': 1641,
    'Lyon': 1649,
    'Lille': 1643,
    'Monaco': 1653,
    'AS Monaco': 1653,
    'Nice': 1661,
    'Lens': 1648,
    'Rennes': 1658,
    'Strasbourg': 1659,
    'Toulouse': 1681,
    'Lorient': 1656,
    'Brest': 1715,
    'Angers': 1684,
    'Nantes': 1647,
    'Auxerre': 1646,
    'Metz': 1651,
    'Paris FC': 6070,
    'Le Havre': 1662,
}

def get_team_logo_url(team_name):
    """Retorna a URL do escudo do time"""
    # Primeiro tenta busca exata
    team_id = TEAM_IDS.get(team_name)
    
    # Se não encontrar, tenta busca parcial (case-insensitive)
    if not team_id:
        for key, value in TEAM_IDS.items():
            if team_name.lower() in key.lower() or key.lower() in team_name.lower():
                team_id = value
                break
    
    if team_id:
        return f"https://img.sofascore.com/api/v1/team/{team_id}/image"
    return None

def get_team_logo_html(team_name, size="20px"):
    """Retorna o HTML completo da tag img para o escudo do time"""
    logo_url = get_team_logo_url(team_name)
    if logo_url:
        return f'<img src="{logo_url}" alt="{team_name}" style="width: {size}; height: {size}; object-fit: cover; vertical-align: middle; margin-right: 5px;">'
    return ''
