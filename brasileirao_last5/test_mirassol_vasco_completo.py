from sofascore_to_html import extrair_h2h_confronto_direto, calcular_pontos_h2h

print('=== TESTE COMPLETO: MIRASSOL VS VASCO ===\n')

# Testa Mirassol vs Vasco
resultados_mirassol = extrair_h2h_confronto_direto('Mirassol', 'Vasco', debug=False)
pontos_mirassol = calcular_pontos_h2h(resultados_mirassol)

print(f'Mirassol vs Vasco:')
print(f'  Resultados: {resultados_mirassol}')
print(f'  Pontos: {pontos_mirassol}')

# Inverte para Vasco
resultados_vasco = []
for res in resultados_mirassol:
    if res == 'V':
        resultados_vasco.append('D')
    elif res == 'D':
        resultados_vasco.append('V')
    else:
        resultados_vasco.append(res)

pontos_vasco = calcular_pontos_h2h(resultados_vasco)

print(f'\nVasco vs Mirassol:')
print(f'  Resultados: {resultados_vasco}')
print(f'  Pontos: {pontos_vasco}')

print('\n=== TABELA H2H ===')
print('Time       | 1 | 2 | 3 | 4 | 5 | Pts')
print('-' * 45)
print(f'Mirassol   | {" | ".join(resultados_mirassol)} | {pontos_mirassol:+.1f}')
print(f'Vasco      | {" | ".join(resultados_vasco)} | {pontos_vasco:+.1f}')
