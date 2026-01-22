import re

# Exemplo do texto que aparece no SofaScore
texto_exemplo = """16/01/26
F2°T
PSG
Lille
3
3
0
0
L"""

print("=" * 50)
print("TEXTO COMPLETO:")
print(texto_exemplo)
print("=" * 50)

# Removendo a data
date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', texto_exemplo)
if date_match:
    print(f"\nData encontrada: {date_match.group(1)}")
    text_without_date = texto_exemplo.replace(date_match.group(0), "")
    print(f"\nTexto sem data:")
    print(text_without_date)
    print("=" * 50)
    
    # Padrão atual (ERRADO)
    score_match_atual = re.search(r'(\d+)\s+(\d+)', text_without_date)
    if score_match_atual:
        print(f"\n❌ PADRÃO ATUAL (ERRADO):")
        print(f"   Regex: (\\d+)\\s+(\\d+)")
        print(f"   Placar extraído: {score_match_atual.group(1)} x {score_match_atual.group(2)}")
    
    # Extrair todos os números
    all_numbers = re.findall(r'\d+', text_without_date)
    print(f"\n📊 TODOS OS NÚMEROS ENCONTRADOS:")
    for i, num in enumerate(all_numbers):
        print(f"   Posição {i}: {num}")
    
    # Placar correto esperado PSG 3 x 0 Lille
    print(f"\n✅ PLACAR CORRETO ESPERADO: PSG 3 x 0 Lille")
    
    # Remover o número do status (F2°T, etc)
    text_clean = re.sub(r'F\d+°T', '', text_without_date)
    print(f"\nTexto limpo (sem status):")
    print(text_clean)
    
    # Extrair novamente
    clean_numbers = re.findall(r'\d+', text_clean)
    print(f"\n📊 NÚMEROS APÓS LIMPAR:")
    for i, num in enumerate(clean_numbers):
        print(f"   Posição {i}: {num}")
    
    if len(clean_numbers) >= 2:
        print(f"\n✅ SOLUÇÃO 1 - Primeiros 2 números: {clean_numbers[0]} x {clean_numbers[1]}")
    
    if len(clean_numbers) >= 4:
        print(f"✅ SOLUÇÃO 2 - Posições 0 e 2: {clean_numbers[0]} x {clean_numbers[2]}")
        print(f"✅ SOLUÇÃO 3 - Posições 1 e 3: {clean_numbers[1]} x {clean_numbers[3]}")
