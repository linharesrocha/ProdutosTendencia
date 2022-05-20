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
    data_grow['Media-Preco'] = 0
    data_grow['Qnt-Normal'] = 0
    data_grow['Qnt-FULL'] = 0
    data_grow['Vendas'] = 0

    return data_grow



def pagina_pesquisa_produto(data_grow):

    # QUANDO BUSCA O PRODUTO E RETORNA TODAS AS OPÇÕES
    # for i in range(len(data_grow)):
    for i in range(2):
        url = data_grow.loc[i, "Link"]
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
            # Redirecionando FULL
            navegador.get(url + "_Frete_Full")

            # Salvando a página
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')

            # Quantidade de anúncios FULL
            product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

            # Volta Página
            navegador.get(url)
        except AttributeError:
            product_full_quantity = 'NaoTem'

            # Volta Página
            navegador.get(url)
            sleep(1)

            # Salvando a página
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')



        print('Quantidade Full ' + product_full_quantity)
        print('Quantidade Normal ' + product_normal_quantity)


        # TODOS OS PRODUTOS
        container = site.find(class_='ui-search-results')
        product_container = container.findAll('li', class_='ui-search-layout__item')
        product_link = [p.find('a', href=True).get('href') for p in product_container]

        products_price = []
        products_sales = []

        # ACESSA CADA PRODUTO DENTRO DE ALGUMA CATEGORIA/PRODUTO TENDENCIA
        # TIRAR MEDIA DE QUANTIDADE DE VENDAS, PRECO

        # products_length = len(product_link)
        # for i in range(products_length):
        #     print('{} / {}'.format(i, products_length))
        for i in range(2):
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
                # Cleaning sales name and string
                products_sales_clean = re.findall('[0-9]+', sales)

                # List to String
                products_sales_clean = ''.join(map(str, products_sales_clean))
                products_sales.append(products_sales_clean)
            else:
                products_sales.append('0')


    # Price
    products_price_list = list(map(int, products_price))
    # Sales
    products_sales_list = list(map(int, products_sales))

    products_sales = statistics.mean(products_sales_list)
    products_price = statistics.mean(products_price_list)

    data_grow.loc[i, 'Qnt-Normal'] = product_normal_quantity
    data_grow.loc[i, 'Qnt-FULL'] = product_full_quantity
    data_grow.loc[i, 'Media-Preco'] = products_price
    data_grow.loc[i, 'Vendas'] = products_sales

    data_grow.to_excel("produtos.xlsx", index=False, encoding='utf-8')


if __name__ == "__main__":
    pagina_gategoria_tendencia()
    pagina_pesquisa_produto(data_grow)