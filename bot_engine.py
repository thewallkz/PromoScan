import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# === LISTA NEGRA DE PALAVRAS ===
TERMOS_USADOS = [
    "usado", "recondicionado", "vitrine", "seminovo", "semi-novo", 
    "renewed", "renovado", "grade a", "grade b", "grade c", 
    "outlet", "open box", "reembalado", "mostruário", "sucata", "peças"
]

def iniciar_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# === FUNÇÃO AUXILIAR DE FILTRO ===
def eh_produto_usado(titulo):
    """Retorna True se o título contiver palavras de produtos usados"""
    titulo_lower = titulo.lower()
    for termo in TERMOS_USADOS:
        # Verifica se o termo está no título (ex: "iPhone Vitrine" contém "vitrine")
        if termo in titulo_lower:
            return True
    return False

# === 1. MERCADO LIVRE ===
def extrair_mercadolivre(driver, termo_busca, preco_maximo, somente_novos):
    print(">>> Indo para Mercado Livre...")
    try:
        termo_url = termo_busca.replace(" ", "-")
        url = f"https://lista.mercadolivre.com.br/{termo_url}_Condicion_Nuevo" # Tenta filtrar via URL também
        driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        produtos = []
        
        itens = soup.find_all('li', class_='ui-search-layout__item')
        if not itens: itens = soup.find_all('div', class_='ui-search-result__wrapper')
        if not itens: itens = soup.find_all('div', class_='andes-card') 

        for item in itens:
            try:
                titulo_elem = item.find('h2', class_='ui-search-item__title') or item.find('a', class_='poly-component__title') or item.find('h2', class_='poly-component__title')
                if not titulo_elem: titulo_elem = item.find('h2')
                if not titulo_elem: continue
                titulo = titulo_elem.text.strip()
                
                # --- FILTRO DE USADOS ---
                if somente_novos and eh_produto_usado(titulo):
                    continue # Pula este item

                link_elem = item.find('a', class_='ui-search-link') or item.find('a', class_='poly-component__title-link')
                link = "#"
                if link_elem: link = link_elem['href']
                elif titulo_elem.name == 'a': link = titulo_elem.get('href', '#')

                img_url = "https://http2.mlstatic.com/frontend-assets/ui-navigation/5.18.9/mercadolibre/logo__large_plus.png"
                img_elem = item.find('img')
                if img_elem: img_url = img_elem.get('data-src') or img_elem.get('src')

                preco_pix = 0.0
                preco_container = item.find('div', class_='poly-price__current') or item.find('div', class_='ui-search-price__second-line') or item
                precos_spans = preco_container.find_all('span', class_='andes-money-amount__fraction')
                if precos_spans:
                    val_txt = precos_spans[-1].text.replace('.', '').replace(',', '.')
                    preco_pix = float(val_txt)

                preco_cartao = preco_pix
                parcelas_txt = "À vista"
                
                installments = item.find('span', class_='poly-price__installments') or item.find('div', class_='ui-search-installments')
                if installments:
                    txt = installments.text.strip()
                    match = re.search(r'(\d+)x.*?R\$\s*([\d\.,]+)', txt)
                    if match:
                        qtd = int(match.group(1))
                        val = float(match.group(2).replace('.', '').replace(',', '.'))
                        preco_cartao = qtd * val
                        parcelas_txt = f"{qtd}x de R$ {val:,.2f}"

                if preco_pix > 0 and preco_cartao <= preco_maximo:
                    produtos.append({
                        "titulo": titulo,
                        "imagem": img_url,
                        "val_sort": preco_pix,
                        "preco_pix": f"{preco_pix:,.2f}",
                        "preco_cartao": f"{preco_cartao:,.2f}",
                        "info_parcelas": parcelas_txt,
                        "link": link,
                        "loja": "Mercado Livre"
                    })
            except: continue
        return produtos
    except Exception as e:
        print(f"Erro ML: {e}")
        return []

# === 2. AMAZON ===
def extrair_amazon(driver, termo_busca, preco_maximo, somente_novos):
    print(">>> Indo para Amazon...")
    try:
        termo_url = termo_busca.replace(" ", "+")
        # Na Amazon, adicionamos &rh=p_n_condition-type%3A13862762011 para forçar 'Novo' via URL
        filtro_url = "&rh=p_n_condition-type%3A13862762011" if somente_novos else ""
        url = f"https://www.amazon.com.br/s?k={termo_url}{filtro_url}"
        
        driver.get(url)
        time.sleep(3) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        produtos = []
        itens = soup.find_all('div', {'data-component-type': 's-search-result'})

        for item in itens:
            try:
                titulo_elem = item.find('span', class_='a-text-normal')
                if not titulo_elem: continue
                titulo = titulo_elem.text.strip()
                
                # --- FILTRO DE USADOS (Dupla segurança: URL + Texto) ---
                if somente_novos and eh_produto_usado(titulo):
                    continue

                link_elem = item.find('a', class_='a-link-normal')
                link = "https://www.amazon.com.br" + link_elem['href'] if link_elem else "#"

                img_elem = item.find('img', class_='s-image')
                img_url = img_elem['src'] if img_elem else ""

                valor_final = 0.0
                texto_cartao = item.get_text()
                
                padroes = [r'R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})', r'R\$\s?(\d{1,3}(?:\.\d{3})*)']
                for padrao in padroes:
                    match = re.search(padrao, texto_cartao)
                    if match:
                        limpo = match.group(1).replace(".", "").replace(",", ".")
                        try:
                            temp_val = float(limpo)
                            if temp_val > 5: 
                                valor_final = temp_val
                                break
                        except: continue

                if valor_final > 0 and valor_final <= preco_maximo:
                    produtos.append({
                        "titulo": titulo,
                        "imagem": img_url,
                        "val_sort": valor_final,
                        "preco_pix": f"{valor_final:,.2f}",
                        "preco_cartao": f"{valor_final:,.2f}",
                        "info_parcelas": "Ver site",
                        "link": link,
                        "loja": "Amazon"
                    })
            except: continue
        return produtos
    except Exception as e:
        print(f"Erro Amazon: {e}")
        return []

# === 3. MAGAZINE LUIZA ===
def extrair_magalu(driver, termo_busca, preco_maximo, somente_novos):
    print(">>> Indo para Magazine Luiza...")
    try:
        termo_url = termo_busca.replace(" ", "+")
        url = f"https://www.magazineluiza.com.br/busca/{termo_url}/"
        driver.get(url)
        time.sleep(3) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        produtos = []
        itens = soup.find_all('a', {'data-testid': 'product-card-container'})

        for item in itens:
            try:
                titulo_elem = item.find('h2', {'data-testid': 'product-title'})
                if not titulo_elem: continue
                titulo = titulo_elem.text.strip()
                
                # --- FILTRO DE USADOS ---
                if somente_novos and eh_produto_usado(titulo):
                    continue

                link_relativo = item['href']
                link = "https://www.magazineluiza.com.br" + link_relativo if link_relativo.startswith('/') else link_relativo
                
                img_url = ""

                texto_todo = item.get_text()
                matches = re.findall(r'R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})', texto_todo)
                todos_valores = []
                for m in matches:
                    try: todos_valores.append(float(m.replace(".", "").replace(",", ".")))
                    except: continue
                
                if not todos_valores: continue

                val_parcela_individual = 0.0
                match_parc = re.search(r'(\d+)x\s*de\s*R\$\s*([\d\.,]+)', texto_todo)
                parcelas_txt = "Ver site"
                if match_parc:
                    qtd = int(match_parc.group(1))
                    val_parcela_individual = float(match_parc.group(2).replace('.', '').replace(',', '.'))
                    parcelas_txt = f"{qtd}x de R$ {val_parcela_individual:,.2f}"

                valores_candidatos = [v for v in todos_valores if abs(v - val_parcela_individual) > 0.01]
                valor_final = min(valores_candidatos) if valores_candidatos else min(todos_valores)
                
                valor_total_cartao = val_parcela_individual * (int(match_parc.group(1)) if match_parc else 1)
                if valor_total_cartao < valor_final: valor_total_cartao = valor_final

                if valor_final > 0 and valor_final <= preco_maximo:
                    produtos.append({
                        "titulo": titulo,
                        "imagem": img_url,
                        "val_sort": valor_final,
                        "preco_pix": f"{valor_final:,.2f}",
                        "preco_cartao": f"{valor_total_cartao:,.2f}",
                        "info_parcelas": parcelas_txt,
                        "link": link,
                        "loja": "Magazine Luiza"
                    })
            except: continue
        return produtos
    except Exception as e:
        print(f"Erro Magalu: {e}")
        return []

# === MAIN ===
def buscar_produtos(termo_busca, preco_maximo, loja='ml', somente_novos=True):
    print(f"🚀 Iniciando busca. Filtro Novos: {somente_novos}")
    driver = iniciar_driver()
    resultados = []

    try:
        if loja == 'todas':
            resultados.extend(extrair_mercadolivre(driver, termo_busca, preco_maximo, somente_novos))
            resultados.extend(extrair_amazon(driver, termo_busca, preco_maximo, somente_novos))
            resultados.extend(extrair_magalu(driver, termo_busca, preco_maximo, somente_novos))
        
        elif loja == 'amazon':
            resultados = extrair_amazon(driver, termo_busca, preco_maximo, somente_novos)
        elif loja == 'magalu':
            resultados = extrair_magalu(driver, termo_busca, preco_maximo, somente_novos)
        else:
            resultados = extrair_mercadolivre(driver, termo_busca, preco_maximo, somente_novos)
            
    except Exception as e:
        print(f"Erro Crítico no Loop: {e}")
    finally:
        driver.quit()

    return resultados