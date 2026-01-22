#!/usr/bin/env python3
import sys
sys.path.insert(0, 'd:/Pesquisa BET/brasileirao_last5')

from gerar_html_ligue1 import times_correspondem

# Teste de correspondência
print("Teste da função times_correspondem():")
print(f"  'Strasbourg' == 'Strasbourg': {times_correspondem('Strasbourg', 'Strasbourg')}")
print(f"  'Strasbourg' == 'strasbourg': {times_correspondem('Strasbourg', 'strasbourg')}")
print(f"  'Strasbourg' == 'Metz': {times_correspondem('Strasbourg', 'Metz')}")

# Teste com jogo real
jogo_test = {
    'mandante': 'Strasbourg',
    'visitante': 'Metz',
    'placar_mandante': 2,
    'placar_visitante': 1
}

team_name = 'Strasbourg'
e_casa = times_correspondem(team_name, jogo_test['mandante'])
e_fora = times_correspondem(team_name, jogo_test['visitante'])

print(f"\nJogo: Strasbourg 2 x 1 Metz")
print(f"  Team procurado: '{team_name}'")
print(f"  É casa? {e_casa}")
print(f"  É fora? {e_fora}")

if e_casa:
    if jogo_test['placar_mandante'] > jogo_test['placar_visitante']:
        print(f"  Classe CSS: vitoria")
    else:
        print(f"  Classe CSS: derrota ou empate")
