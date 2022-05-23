# Imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from SQL.sql import start_sqlite
import pandas as pd
from datetime import datetime
import statistics
import re
import os
import streamlit as st


# Functions
def waituntil(driver, class_):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, class_))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print('Timed out waiting for page to load')
        print('Trying again')
        driver.refresh()
        element_present = EC.presence_of_element_located((By.CLASS_NAME, class_))
        WebDriverWait(driver, 10).until(element_present)


def pagina_tendencias():
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

    waituntil(navegador, 'ui-search-entry-keyword')
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    page_trends = site.findAll(class_="ui-search-carousel")

    aux = 0
    for x in range(len(page_trends)):
        # Pegando produtos
        category_trends = page_trends[x].findAll('div', class_='entry-column')
        for product in category_trends:
            data.loc[aux, 'Posicao'] = product.find('div', class_='ui-search-entry-description').getText()
            data.loc[aux, 'Nome'] = product.find('h3', class_='ui-search-entry-keyword').getText()
            data.loc[aux, 'Link'] = product.find('a', href=True).get('href').replace('#trend', '')
            aux += 1

    data['Qnt_Normal'] = 0
    data['Qnt_FULL'] = 0
    data['Media_Preco'] = 0
    data['Mediana_Preco'] = 0
    data['Media_Vendas'] = 0
    data['Mediana_Vendas'] = 0
    data['GoogleTrends'] = 'NA'
    data['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return data

    navegador.quit()


def pagina_produtos(data):
    # ACESSA CADA PRODUTO TENDENDIA, -> 1PRIMEIRO PRODUTO TENDENCIA, 2PRODUTO TENDENCIAS E
    # ACESSA TODOS ELES UM DE CADA VEZ
    for z in range(len(data)):
    #for z in range(2):
        print("{} / {}".format(z, len(data)))

        url = data.loc[z, "Link"]
        navegador.get(url)

        waituntil(navegador, 'ui-search-search-result__quantity-results')
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Qntd anúncios normal
        product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
        product_normal_quantity = int(re.search(r'\d+', product_normal_quantity).group())

        try:
            navegador.get(url + "_Frete_Full")
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
            product_full_quantity = int(re.search(r'\d+', product_full_quantity).group())
        except AttributeError:
            product_full_quantity = 0

        navegador.get(url)
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')
        waituntil(navegador, 'ui-search-result__bookmark')

        # TODOS OS PRODUTOS DA CATEGORIA ATUAL
        container = site.find(class_='ui-search-results')
        product_container = container.findAll('li', class_='ui-search-layout__item')
        product_link = [p.find('a', href=True).get('href') for p in product_container]
        products_price = []
        products_sales = []

        # ACESSA CADA PRODUTO DENTRO DA ATUAL CATEGORIA/TENDENCIA
        # TIRAR MEDIA DE QUANTIDADE DE VENDAS, PRECO
        products_length = len(product_link)
        products_length = round(products_length / 3)
        for i in range(products_length):
        #for i in range(3):
            navegador.get(product_link[i])
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product = site.find(class_='pb-40')

            price_fraction = product.find('span', class_='andes-money-amount__fraction').getText().replace('.', '')
            products_price.append(price_fraction)

            sales = product.find('span', class_='ui-pdp-subtitle').getText()
            if sales != 'Novo':  # Diferente de 0 Vendas
                products_sales_clean = re.findall('[0-9]+', sales)
                products_sales_clean = ''.join(map(str, products_sales_clean))
                products_sales.append(products_sales_clean)
            else:
                products_sales.append('0')

        # MANIPULANDO DADOS
        products_price = list(map(int, products_price))
        products_sales = list(map(int, products_sales))
        products_sales_mean = int(statistics.mean(products_sales))
        products_sales_median = int(statistics.median(products_sales))
        products_price_mean = round(int(statistics.mean(products_price)), 2)
        products_price_median = round(statistics.median(products_price), 2)

        # CRIANDO NOVAS COLUNAS
        data.loc[z, 'Qnt_Normal'] = product_normal_quantity
        data.loc[z, 'Qnt_FULL'] = product_full_quantity
        data.loc[z, 'Media_Preco'] = products_price_mean
        data.loc[z, 'Mediana_Preco'] = products_price_median
        data.loc[z, 'Media_Vendas'] = products_sales_mean
        data.loc[z, 'Mediana_Vendas'] = products_sales_median

        url_gtrends = "https://trends.google.com.br/trends/explore?geo=BR&q="
        name_product = data.loc[z, 'Nome']
        data.loc[z, 'GoogleTrends'] = url_gtrends + name_product

    return data
    navegador.quit()


def transformacao(data):
    global data_crescimento
    global data_desejada
    global data_popular

    # REORDENANDO COLUNAS
    data = data[['Posicao', 'Nome', 'Qnt_Normal', 'Qnt_FULL',
                 'Media_Preco', 'Mediana_Preco', 'Media_Vendas', 'Mediana_Vendas',
                 'Link', 'GoogleTrends', 'scrapy_datetime']]

    # CRIANDO 3 DATAFRAMES DIFERENTES
    data_crescimento = data.loc[data['Posicao'].str.contains('CRESCIMENTO')]
    data_desejada = data.loc[data['Posicao'].str.contains('DESEJADA')]
    data_popular = data.loc[data['Posicao'].str.contains('POPULAR')]

    # REMOVENDO STRING E CONVERTENDO POSICAO PARA INT
    data_crescimento['Posicao'] = data_crescimento['Posicao'].str.extract('(\d+)').astype(int)
    data_desejada['Posicao'] = data_desejada['Posicao'].str.extract('(\d+)').astype(int)
    data_popular['Posicao'] = data_popular['Posicao'].str.extract('(\d+)').astype(int)


def start_streamlit():
    st.title("Produtos que mais Cresceram")
    st.write(data_crescimento)
    st.title("Produtos mais Desejados")
    st.write(data_desejada)
    st.title("Produtos mais Populares")
    st.write(data_popular)

if __name__ == "__main__":
    # Settings Driver
    pd.set_option('mode.chained_assignment', None)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    navegador = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    navegador.maximize_window()


    # Settings Streamlit
    st.set_page_config(page_title='Tendencias', layout='wide')

    pagina_tendencias()
    pagina_produtos(data)
    transformacao(data)
    start_streamlit()
