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
import statistics
import re

# Configurações
option = Options()
option.headless = True
navegador = webdriver.Firefox(options=option)
navegador.maximize_window()

def pagina_gategoria_tendencia():

    global data
    data = pd.DataFrame()
    data['Posicao'] = 'NA'
    data['Nome'] = 'NA'
    data['Link'] = 'NA'


    url = "https://tendencias.mercadolivre.com.br/1276-esportes_e_fitness"
    # Iniciando Navegador
    navegador.get(url)
    # Descendo a pagina para carregar todos os produtos
    body = navegador.find_element(By.CSS_SELECTOR, "body")
    for i in range(1, 20):
        body.send_keys(Keys.PAGE_DOWN)
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ui-search-entry-keyword'))
        WebDriverWait(navegador, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    page_trends = site.findAll(class_="ui-search-carousel")

    aux = 0
    for x in range(len(page_trends)):
        # Pegando produtos
        category_trends = page_trends[x].findAll('div', class_='entry-column')

        # Buscando produtos
        for product in category_trends:
            data.loc[aux, 'Posicao'] = product.find('div', class_='ui-search-entry-description').getText()
            data.loc[aux, 'Nome'] = product.find('h3', class_='ui-search-entry-keyword').getText()
            data.loc[aux, 'Link'] = product.find('a', href=True).get('href').replace('#trend', '')
            aux += 1

    data['Qnt-Normal'] = 0
    data['Qnt-FULL'] = 0
    data['Media-Preco'] = 0
    data['Mediana-Preco'] = 0
    data['Media-Vendas'] = 0
    data['Mediana-Vendas'] = 0
    data['GoogleTrends'] = 'NA'
    data['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data.to_excel("produtos.xlsx", index=False, encoding='utf-8')

    return data

def pagina_pesquisa_produto(data):

    # ACESSA CADA PRODUTO TENDENDIA, -> 1PRIMEIRO PRODUTO TENDENCIA, 2PRODUTO TENDENCIAS E
    # ACESSA TODOS ELES UM DE CADA VEZ
    #for z in range(len(data)):
    for z in range(2):
        url = data.loc[z, "Link"]
        print(url)

        navegador.get(url)

        body = navegador.find_element(By.CSS_SELECTOR, "body")

        for i in range(1, 20):
            body.send_keys(Keys.PAGE_DOWN)

        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ui-search-search-result__quantity-results'))
            WebDriverWait(navegador, 10).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

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

        products_sales_mean = round(statistics.mean(products_sales_list), 2)
        products_price_mean = round(statistics.mean(products_price_list),2)
        products_sales_median = round(statistics.median(products_sales_list),2)
        products_price_median = round(statistics.median(products_price_list),2)

        data.loc[z, 'Qnt-Normal'] = product_normal_quantity
        data.loc[z, 'Qnt-FULL'] = product_full_quantity
        data.loc[z, 'Media-Preco'] = products_price_mean
        data.loc[z, 'Mediana-Preco'] = products_price_median
        data.loc[z, 'Media-Vendas'] = products_sales_mean
        data.loc[z, 'Mediana-Vendas'] = products_sales_median

        url_gtrends = "https://trends.google.com.br/trends/explore?geo=BR&q="
        name_product = data.loc[z, 'Nome']
        data.loc[z, 'GoogleTrends'] = url_gtrends + name_product

        data.to_excel("produtos.xlsx", index=False, encoding='utf-8')


if __name__ == "__main__":
    pagina_gategoria_tendencia()
    #pagina_pesquisa_produto(data)