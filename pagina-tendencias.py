from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
from time import sleep
import statistics
import re

# Configurações
option = Options()
option.headless = False
navegador = webdriver.Firefox(options=option)
navegador.maximize_window()

def pagina_gategoria_tendencia():

    global data_grow
    url = "https://tendencias.mercadolivre.com.br/1276-esportes_e_fitness"

    # Iniciando Navegador
    navegador.get(url)
    sleep(2)

    # Descendo a pagina para carregar todos os produtos
    body = navegador.find_element(By.CSS_SELECTOR, "body")

    for i in range(1, 20):
        body.send_keys(Keys.PAGE_DOWN)
    sleep(4)

    # Salvando a página
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    # Carrousel -> As buscas que mais cresceram
    carrousel_grow = site.find(class_="ui-search-carousel")

    # Pegando produtos -> As buscas que mais cresceram
    product_list = carrousel_grow.findAll('div', class_='entry-column')

    # Buscando produtos e salvando em uma lista
    product_position_grow = [p.find('div', class_ = 'ui-search-entry-description').getText().replace('º MAIOR CRESCIMENTO', '') for p in product_list]
    product_name_grow = [p.find('p', class_ = 'ui-search-entry-keyword').getText() for p in product_list]
    product_link_grow = [p.find('a', href=True).get('href').replace('#trend', '') for p in product_list]

    # DataFrame
    data_grow = pd.DataFrame([product_position_grow, product_name_grow, product_link_grow]).T
    data_grow.columns = ['Posicao', 'Nome', 'Link']
    data_grow['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return data_grow


def pagina_pesquisa_produto(data_grow):
    data_grow['Media-Preco'] = 0
    data_grow['Qnt Normal'] = 0
    data_grow['Qnt FULL'] = 0
    data_grow['Vendas'] = 0

    url = "https://lista.mercadolivre.com.br/bbs-airsoft"

    # Iniciando Navegador
    navegador.get(url)
    sleep(2)

    # Descendo a pagina para carregar todos os produtos
    body = navegador.find_element(By.CSS_SELECTOR, "body")

    for i in range(1, 20):
        body.send_keys(Keys.PAGE_DOWN)
    sleep(4)

    # Salvando a página
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    # Quantidade de anúncios normal
    product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()


    container = site.find(class_='ui-search-results')
    product_container = container.findAll('li', class_='ui-search-layout__item')

    # Link de Cada produto
    product_link = [p.find('a', href=True).get('href') for p in product_container]

    products_price = []
    products_sales = []

    # Acessa cada produto do Container da Categoria
    products_length = len(product_link)
    # for i in range(products_length):
    #     print('{} / {}'.format(i, products_length))
    for i in range(5):
        print('{} / {}'.format(i, 5))
        navegador.get(product_link[i])
        sleep(1)

        # Salva pagina
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        product_side_info = site.find(class_='pl-16')
        price_fraction = product_side_info.find('span', class_='andes-money-amount__fraction').getText()
        sales = product_side_info.find('span', class_='ui-pdp-subtitle').getText()

        products_price.append(price_fraction)
        products_sales.append(sales)

    # String p/ Int Price and Mean/Median
    products_price_list = list(map(int, products_price))
    print(products_price_list)
    products_price = statistics.mean(products_price_list)
    print(products_price)

    # Sales Clean and Int/Mean
    products_sales_clean = re.findall('[0-9]+', products_sales)
    products_sales_list = list(map(int, products_sales_clean))
    products_sales = statistics.mean(products_sales_list)


    # Redirecionando FULL
    navegador.get(url + "_Frete_Full")

    # Salvando a página
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    # Quantidade de anúncios FULL
    product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

    data_grow['Media-Preco'][0] = products_price
    data_grow['Qnt Normal'][0] = product_normal_quantity
    data_grow['Qnt FULL'][0] = product_full_quantity
    data_grow['Vendas'][0] = products_sales

    data_grow.to_excel("produto.xlsx")



if __name__ == "__main__":
    pagina_gategoria_tendencia()
    pagina_pesquisa_produto(data_grow)