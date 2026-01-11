"""
Script para descobrir os IDs corretos de Cruzeiro, Palmeiras e Athletico-PR no ogol.com.br
"""
from playwright.sync_api import sync_playwright
import time

def descobrir_id_time(nome_time, slug_busca):
    """Tenta descobrir o ID de um time no ogol.com.br"""
    print(f"\n{'='*80}")
    print(f"Procurando ID para: {nome_time}")
    print(f"{'='*80}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Tenta acessar a página principal do time
        url = f"https://www.ogol.com.br/equipe/{slug_busca}/"
        print(f"URL: {url}")
        
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)
            
            # Tenta encontrar o link "Histórico vs Equipes"
            # Este link geralmente tem o formato: /equipe/{slug}/historico-vs-equipes
            # O ID aparece quando você seleciona um adversário na página
            
            # Vamos tentar pegar o ID da própria URL da página
            # ou procurar por links que contenham ?fk_adv=
            
            # Método 1: Procurar no HTML por padrões de ID
            content = page.content()
            
            # Procurar por padrões como fk_adv=XXXX ou id_team=XXXX
            import re
            
            # Procurar por fk_adv na página
            matches_fk = re.findall(r'fk_adv=(\d+)', content)
            if matches_fk:
                print(f"IDs encontrados via fk_adv: {set(matches_fk)}")
            
            # Procurar por id_equipa ou id_team
            matches_id = re.findall(r'id_equipa["\']?\s*:\s*["\']?(\d+)', content)
            if matches_id:
                print(f"IDs encontrados via id_equipa: {set(matches_id)}")
            
            # Método 2: Acessar a página de histórico vs equipes
            hist_url = f"https://www.ogol.com.br/equipe/{slug_busca}/historico-vs-equipes"
            print(f"\nTentando: {hist_url}")
            page.goto(hist_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)
            
            # Procurar por select/dropdown com lista de adversários
            # Geralmente tem <option value="ID">Nome do Time</option>
            options_script = """
            () => {
                const selects = document.querySelectorAll('select');
                const results = [];
                selects.forEach(select => {
                    const options = select.querySelectorAll('option');
                    options.forEach(opt => {
                        if (opt.value && opt.value.match(/^\d+$/)) {
                            results.push({
                                value: opt.value,
                                text: opt.textContent.trim()
                            });
                        }
                    });
                });
                return results;
            }
            """
            
            options = page.evaluate(options_script)
            if options:
                print(f"\nOPÇÕES ENCONTRADAS NO SELECT (ID: Nome):")
                print("-" * 80)
                for opt in options[:20]:  # Mostrar primeiras 20
                    print(f"  ID {opt['value']}: {opt['text']}")
                
                # Procurar especificamente por Cruzeiro, Palmeiras e Athletico-PR
                for opt in options:
                    if any(termo in opt['text'].lower() for termo in ['cruzeiro', 'palmeiras', 'athletico', 'atlético-pr', 'athletico-pr']):
                        print(f"\n>>> POSSÍVEL MATCH: ID {opt['value']}: {opt['text']}")
            
            print("\nPágina carregada. Inspecione visualmente...")
            input("\nPressione ENTER para continuar...")
            
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Tentar descobrir IDs dos times problemáticos
    times_buscar = [
        ("Cruzeiro", "cruzeiro"),
        ("Palmeiras", "palmeiras"),
        ("Athletico-PR", "atletico-paranaense"),
    ]
    
    for nome, slug in times_buscar:
        descobrir_id_time(nome, slug)
        print("\n" * 3)
