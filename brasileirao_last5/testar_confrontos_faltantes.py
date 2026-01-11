#!/usr/bin/env python3
"""
Testa os 4 confrontos que retornaram 0 jogos
"""

from playwright.sync_api import sync_playwright
import time

def testar_confronto(slug_time1, id_time2, nome_confronto):
    """Testa um confronto específico"""
    url = f"https://www.ogol.com.br/equipe/{slug_time1}/historico-vs-equipes?fk_adv={id_time2}"
    print(f"\n{'='*80}")
    print(f"Testando: {nome_confronto}")
    print(f"URL: {url}")
    print('='*80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(3)
            
            # Extrai os jogos
            jogos = page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('tr');
                    const games = [];
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length > 0) {
                            const text = row.innerText;
                            if (text && (text.match(/\\d{4}-\\d{2}-\\d{2}/) || text.match(/\\d{2}\\/\\d{2}\\/\\d{4}/))) {
                                games.push(text.trim());
                            }
                        }
                    });
                    return games;
                }
            """)
            
            print(f"Encontrados {len(jogos)} jogos")
            if len(jogos) > 0:
                print("\nPrimeiros 5 jogos:")
                for i, jogo in enumerate(jogos[:5], 1):
                    print(f"  {i}. {jogo}")
            else:
                print("❌ Nenhum jogo encontrado!")
                
                # Vamos ver o que tem na página
                print("\nConteúdo da página:")
                conteudo = page.evaluate("() => document.body.innerText")
                print(conteudo[:500])
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            browser.close()

# Testa os 4 confrontos
print("\n" + "="*80)
print("TESTANDO CONFRONTOS SEM DADOS")
print("="*80)

# 1. Mirassol vs Vasco
testar_confronto("mirassol", 2258, "Mirassol vs Vasco")

# 2. Coritiba vs Bragantino  
testar_confronto("coritiba", 3156, "Coritiba vs Bragantino")

# 3. Vitória vs Remo
testar_confronto("vitoria", 3423, "Vitória vs Remo")

# 4. Chapecoense vs Santos
testar_confronto("chapecoense", 2254, "Chapecoense vs Santos")

print("\n" + "="*80)
print("TESTES CONCLUÍDOS")
print("="*80)
