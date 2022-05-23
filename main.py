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
import time
import re
import logging
import os


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
    logger.info('Inicio da Coleta de Dados dos Produtos Tendencias')
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
    logger.info('FIM')


def pagina_produtos(data):
    # ACESSA CADA PRODUTO TENDENDIA, -> 1PRIMEIRO PRODUTO TENDENCIA, 2PRODUTO TENDENCIAS E
    # ACESSA TODOS ELES UM DE CADA VEZ
    for z in range(len(data)):
    #for z in range(2):
        # print("{} / {}".format(z, len(data)))
        logger.info('%s de %s', z, len(data))

        url = data.loc[z, "Link"]
        logger.info('Acessando %s', url)
        navegador.get(url)

        waituntil(navegador, 'ui-search-search-result__quantity-results')
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Qntd anúncios normal
        logger.info('Buscando quantidade de anuncios normal')
        product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
        product_normal_quantity = int(re.search(r'\d+', product_normal_quantity).group())

        logger.info('Buscando quantidade de anuncios full')
        try:
            navegador.get(url + "_Frete_Full")
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
            product_full_quantity = int(re.search(r'\d+', product_full_quantity).group())
        except AttributeError:
            product_full_quantity = 0

        logger.info('Retoma pagina de pesquisa')
        navegador.get(url)
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')
        waituntil(navegador, 'ui-search-result__bookmark')

        # TODOS OS PRODUTOS DA CATEGORIA ATUAL
        logger.info('Coleta todos produtos da categoria atual')
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
            logger.info('Acessando cada anuncio para coletar preco e venda')
        #for i in range(3):
            time.sleep(30)
            logger.info('Acessando %s', product_link[i])
            navegador.get(product_link[i])
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product = site.find(class_='pb-40')

            logger.info('Buscando preco e vendas')
            price_fraction = product.find('span', class_='andes-money-amount__fraction').getText().replace('.', '')
            products_price.append(price_fraction)

            sales = product.find('span', class_='ui-pdp-subtitle').getText()
            if sales != 'Novo':  # Diferente de 0 Vendas
                products_sales_clean = re.findall('[0-9]+', sales)
                products_sales_clean = ''.join(map(str, products_sales_clean))
                products_sales.append(products_sales_clean)
            else:
                products_sales.append('0')

            navegador.quit()

        logger.info('Manilupando dados coletados')
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

    logger.info('Transformando dados')
    # REORDENANDO COLUNAS
    data = data[['Posicao', 'Nome', 'Qnt_Normal', 'Qnt_FULL',
                 'Media_Preco', 'Mediana_Preco', 'Media_Vendas', 'Mediana_Vendas',
                 'Link', 'GoogleTrends', 'scrapy_datetime']]

    # CRIANDO 3 DATAFRAMES DIFERENTES
    data_crescimento = data.loc[data['Posicao'].str.contains('CRESCIMENTO')]
    data_desejada = data.loc[data['Posicao'].str.contains('DESEJADA')]
    data_popular = data.loc[data['Posicao'].str.contains('POPULAR')]

    logger.warning('Atualizar esse trecho')
    # REMOVENDO STRING E CONVERTENDO POSICAO PARA INT
    data_crescimento['Posicao'] = data_crescimento['Posicao'].str.extract('(\d+)').astype(int)
    data_desejada['Posicao'] = data_desejada['Posicao'].str.extract('(\d+)').astype(int)
    data_popular['Posicao'] = data_popular['Posicao'].str.extract('(\d+)').astype(int)

    logger.info('Salvando CSV')
    # SALVANDO EXCEL
    data_crescimento.to_csv("CSV/produtos_crescimento.csv", index=False, encoding='utf-8')
    data_desejada.to_csv("CSV/produtos_desejado.csv", index=False, encoding='utf-8')
    data_popular.to_csv("CSV/produtos_popular.csv", index=False, encoding='utf-8')


if __name__ == "__main__":
    # Configurações Driver
    option = Options()
    option.headless = True
    navegador = webdriver.Firefox(options=option)
    navegador.maximize_window()

    # Disable Logs Pandas
    pd.set_option('mode.chained_assignment', None)

    # Mkdir
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    if not os.path.exists('CSV'):
        os.makedirs('CSV')

    #Logging
    logging.basicConfig(filename='Logs/tendencias_ml.txt', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    logger = logging.getLogger('tendencias_ml')

    # Call Functions
    pagina_tendencias()
    pagina_produtos(data)
    transformacao(data)
    #start_sqlite()
    #logger.info('Salvo no SQL')
    logger.info('FIM')
