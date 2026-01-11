#!/usr/bin/env python3
"""
Descobre os IDs corretos dos times verificando manualmente no site
"""

from playwright.sync_api import sync_playwright
import time

def verificar_historico_manual(slug_time1, slug_time2, nome_confronto):
    """Verifica manualmente se há histórico entre dois times"""
    url = f"https://www.ogol.com.br/equipe/{slug_time1}/historico-vs-equipes"
    print(f"\n{'='*80}")
    print(f"Verificando: {nome_confronto}")
    print(f"URL: {url}")
    print('='*80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            print("✓ Página carregada. Aguarde para selecionar o time adversário manualmente...")
            time.sleep(5)
            
            # Procura pelo select/dropdown de times
            select_presente = page.query_selector('select')
            if select_presente:
                print("✓ Dropdown de times encontrado!")
                
                # Extrai as opções disponíveis
                options = page.evaluate("""
                    () => {
                        const select = document.querySelector('select');
                        if (!select) return [];
                        const opts = Array.from(select.options);
                        return opts.map(opt => ({
                            value: opt.value,
                            text: opt.textContent.trim()
                        })).filter(o => o.value !== '');
                    }
                """)
                
                print(f"\nTimes disponíveis no dropdown ({len(options)} times):")
                
                # Procura pelo time adversário
                time2_lower = slug_time2.lower().replace('-', ' ')
                for opt in options:
                    if slug_time2.replace('-', ' ').lower() in opt['text'].lower():
                        print(f"\n✓✓✓ ENCONTRADO: {opt['text']} (ID: {opt['value']}) ✓✓✓")
                
                # Mostra alguns times para referência
                print("\nPrimeiros 20 times:")
                for opt in options[:20]:
                    print(f"  - {opt['text']}: {opt['value']}")
                    
            else:
                print("❌ Dropdown de times NÃO encontrado!")
            
            input("\n\nPressione ENTER para continuar...")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            browser.close()

# Verifica os 4 confrontos
print("\n" + "="*80)
print("VERIFICANDO HISTÓRICOS MANUALMENTE")
print("="*80)

confrontos = [
    ("mirassol", "vasco-da-gama", "Mirassol vs Vasco"),
    ("coritiba", "red-bull-bragantino", "Coritiba vs Bragantino"),
    ("vitoria", "remo", "Vitória vs Remo"),
    ("chapecoense", "santos", "Chapecoense vs Santos")
]

for slug1, slug2, nome in confrontos:
    verificar_historico_manual(slug1, slug2, nome)

print("\n" + "="*80)
print("VERIFICAÇÃO CONCLUÍDA")
print("="*80)
