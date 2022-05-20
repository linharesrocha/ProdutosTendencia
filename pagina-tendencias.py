from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    # Descendo a pagina para carregar todos os produtos
    body = navegador.find_element(By.CSS_SELECTOR, "body")

    for i in range(1, 20):
        body.send_keys(Keys.PAGE_DOWN)

    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ui-search-entry-keyword'))
        print(element_present)
        WebDriverWait(navegador, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    # Carrousel -> As buscas que mais cresceram
    carrousel_grow = site.find(class_="ui-search-carousel")

    # Pegando produtos -> As buscas que mais cresceram
    product_list = carrousel_grow.findAll('div', class_='entry-column')

    # Buscando produtos e salvando em uma lista
    product_position_grow = [p.find('div', class_ = 'ui-search-entry-description').getText().replace('º MAIOR CRESCIMENTO', '') for p in product_list]
    product_name_grow = [p.find('h3', class_ = 'ui-search-entry-keyword').getText() for p in product_list]
    product_link_grow = [p.find('a', href=True).get('href').replace('#trend', '') for p in product_list]

    # DataFrame
    data_grow = pd.DataFrame([product_position_grow, product_name_grow, product_link_grow]).T
    data_grow.columns = ['Posicao', 'Nome', 'Link']
    data_grow['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_grow['Qnt-Normal'] = 0
    data_grow['Qnt-FULL'] = 0
    data_grow['Media-Preco'] = 0
    data_grow['Mediana-Preco'] = 0
    data_grow['Media-Vendas'] = 0
    data_grow['Mediana-Vendas'] = 0
    data_grow['GoogleTrends'] = 'NA'


    return data_grow



def pagina_pesquisa_produto(data_grow):

    # ACESSA CADA PRODUTO TENDENDIA, -> 1PRIMEIRO PRODUTO TENDENCIA, 2PRODUTO TENDENCIAS E
    # ACESSA TODOS ELES UM DE CADA VEZ
    #for z in range(len(data_grow)):
    for z in range(2):
        url = data_grow.loc[z, "Link"]
        print(url)

        navegador.get(url)
        sleep(2)

        body = navegador.find_element(By.CSS_SELECTOR, "body")

        for i in range(1, 20):
            body.send_keys(Keys.PAGE_DOWN)
        sleep(4)

        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Qntd anúncios normal
        product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

        try:
            navegador.get(url + "_Frete_Full")
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')

            # Quantidade de anúncios FULL
            product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

            navegador.get(url)
        except AttributeError:
            product_full_quantity = 'NaoTem'

            navegador.get(url)
            sleep(1)

            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')


        # TODOS OS PRODUTOS
        container = site.find(class_='ui-search-results')
        product_container = container.findAll('li', class_='ui-search-layout__item')
        product_link = [p.find('a', href=True).get('href') for p in product_container]

        products_price = []
        products_sales = []

        # ACESSA CADA PRODUTO DENTRO DE ALGUMA CATEGORIA/TENDENCIA
        # TIRAR MEDIA DE QUANTIDADE DE VENDAS, PRECO

        products_length = len(product_link)
        products_length = round(products_length / 3)
        #for i in range(products_length):
        for i in range(3):
            navegador.get(product_link[i])

            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product_side_info = site.find(class_='pl-16')

            # Caso o preço não esteja na lateral
            try:
                price_fraction = product_side_info.find('span', class_='andes-money-amount__fraction').getText()
                products_price.append(price_fraction)
            except AttributeError:
                price_fraction = site.find('span', class_='andes-money-amount__fraction').getText()
                products_price.append(price_fraction)

            # Caso o número de venda não esteja na lateral
            try:
                sales = product_side_info.find('span', class_='ui-pdp-subtitle').getText()

            except AttributeError:
                sales = site.find('span', class_='ui-pdp-subtitle').getText()

            # Caso não tenha número de vendas
            if sales != 'Novo':
                products_sales_clean = re.findall('[0-9]+', sales)
                products_sales_clean = ''.join(map(str, products_sales_clean))
                products_sales.append(products_sales_clean)
            else:
                products_sales.append('0')


        products_price_list = list(map(int, products_price))
        products_sales_list = list(map(int, products_sales))

        products_sales_mean = statistics.mean(products_sales_list)
        products_price_mean = statistics.mean(products_price_list)
        products_sales_median = statistics.median(products_sales_list)
        products_price_median = statistics.median(products_price_list)

        data_grow.loc[z, 'Qnt-Normal'] = product_normal_quantity
        data_grow.loc[z, 'Qnt-FULL'] = product_full_quantity
        data_grow.loc[z, 'Media-Preco'] = products_price_mean
        data_grow.loc[z, 'Mediana-Preco'] = products_price_median
        data_grow.loc[z, 'Media-Vendas'] = products_sales_mean
        data_grow.loc[z, 'Mediana-Vendas'] = products_sales_median

        url_gtrends = "https://trends.google.com.br/trends/explore?geo=BR&q="
        name_product = data_grow.loc[z, 'Nome']
        data_grow.loc[z, 'GoogleTrends'] = url_gtrends + name_product

        data_grow.to_excel("produtos.xlsx", index=False, encoding='utf-8')


if __name__ == "__main__":
    pagina_gategoria_tendencia()
    pagina_pesquisa_produto(data_grow)