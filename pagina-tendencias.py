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


# Functions
def waituntil(driver, class_):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, class_))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")


# Configurações
option = Options()
option.headless = True
navegador = webdriver.Firefox(options=option)
navegador.maximize_window()


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

    data['Qnt-Normal'] = 0
    data['Qnt-FULL'] = 0
    data['Media-Preco'] = 0
    data['Mediana-Preco'] = 0
    data['Media-Vendas'] = 0
    data['Mediana-Vendas'] = 0
    data['GoogleTrends'] = 'NA'
    data['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return data

    navegador.quit()

def pagina_produtos(data):
    # ACESSA CADA PRODUTO TENDENDIA, -> 1PRIMEIRO PRODUTO TENDENCIA, 2PRODUTO TENDENCIAS E
    # ACESSA TODOS ELES UM DE CADA VEZ
    # for z in range(len(data)):
    for z in range(12):
        # print("{} / {}".format(z, len(data)))

        url = data.loc[z, "Link"]
        navegador.get(url)

        waituntil(navegador, 'ui-search-search-result__quantity-results')
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Qntd anúncios normal
        product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

        try:
            navegador.get(url + "_Frete_Full")
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
        except AttributeError:
            product_full_quantity = 'NaoTem'

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
        # products_length = len(product_link)
        # products_length = round(products_length / 3)
        # for i in range(products_length):
        for i in range(3):
            navegador.get(product_link[i])
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product = site.find(class_='pb-40')

            price_fraction = product.find('span', class_='andes-money-amount__fraction').getText().replace('.', '')
            products_price.append(price_fraction)

            sales = product.find('span', class_='ui-pdp-subtitle').getText()
            if sales != 'Novo': # Diferente de 0 Vendas
                products_sales_clean = re.findall('[0-9]+', sales)
                products_sales_clean = ''.join(map(str, products_sales_clean))
                products_sales.append(products_sales_clean)
            else:
                products_sales.append('0')

        # MANIPULANDO DADOS
        products_price = list(map(int, products_price))
        products_sales = list(map(int, products_sales))
        products_sales_mean = round(statistics.mean(products_sales), 2)
        products_price_mean = round(statistics.mean(products_price), 2)
        products_sales_median = round(statistics.median(products_sales), 2)
        products_price_median = round(statistics.median(products_price), 2)

        # CRIANDO NOVAS COLUNAS
        data.loc[z, 'Qnt-Normal'] = product_normal_quantity
        data.loc[z, 'Qnt-FULL'] = product_full_quantity
        data.loc[z, 'Media-Preco'] = products_price_mean
        data.loc[z, 'Mediana-Preco'] = products_price_median
        data.loc[z, 'Media-Vendas'] = products_sales_mean
        data.loc[z, 'Mediana-Vendas'] = products_sales_median

        url_gtrends = "https://trends.google.com.br/trends/explore?geo=BR&q="
        name_product = data.loc[z, 'Nome']
        data.loc[z, 'GoogleTrends'] = url_gtrends + name_product

        return data
        navegador.quit()

def salvar(data):
    # CRIANDO 3 DATAFRAMES DIFERENTES
    data_crescimento = data.loc[data['Posicao'].str.contains('CRESCIMENTO')]
    data_desejada = data.loc[data['Posicao'].str.contains('DESEJADA')]
    data_popular = data.loc[data['Posicao'].str.contains('POPULAR')]

    # SALVANDO EXCEL
    data_crescimento.to_excel("produtos_crescimento.xlsx", index=False, encoding='utf-8')
    data_desejada.to_excel("produtos_desejado.xlsx", index=False, encoding='utf-8')
    data_popular.to_excel("produtos_popular.xlsx", index=False, encoding='utf-8')


if __name__ == "__main__":
    pagina_tendencias()
    pagina_produtos(data)
    salvar(data)