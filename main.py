# Imports
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
import re
from datetime import date
import slack
import os
from pathlib import Path
from dotenv import load_dotenv


def waituntil(driver, class_):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, class_))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print('Timed out waiting for page to load')


def pagina_tendencias(url_list):
    global data
    data = pd.DataFrame()
    data['Posicao'] = 'NA'
    data['Nome'] = 'NA'
    data['Link_ML'] = 'NA'

    # Iniciando Navegador
    navegador.get(url_list[l])
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
            data.loc[aux, 'Link_ML'] = product.find('a', href=True).get('href').replace('#trend', '')
            aux += 1

    data['Qnt_Normal'] = 0
    data['Qnt_FULL'] = 0
    data['Qnt_Netshoes'] = 0
    data['GoogleTrends'] = 'NA'
    data['UltimaAtualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #return data

    #navegador.quit()


def pagina_produtos(data):
    #for z in range(len(data)):
    for z in range(2):
        url = data.loc[z, "Link_ML"]
        navegador.get(url)

        waituntil(navegador, 'ui-search-search-result__quantity-results')
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Qntd anúncios normal
        product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
        product_normal_quantity = int(re.sub('[^0-9]', '', product_normal_quantity))

        try:
            navegador.get(url + "_Frete_Full")
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
            product_full_quantity = int(re.sub('[^0-9]', '', product_full_quantity))
        except AttributeError:
            product_full_quantity = 0

        # CRIANDO NOVAS COLUNAS
        data.loc[z, 'Qnt_Normal'] = product_normal_quantity
        data.loc[z, 'Qnt_FULL'] = product_full_quantity

        url_gtrends = "https://trends.google.com.br/trends/explore?geo=BR&q="
        name_product = data.loc[z, 'Nome']
        data.loc[z, 'GoogleTrends'] = url_gtrends + name_product

    #navegador.quit()
    return data


def netshoes():
    for i in range(len(data)):
    #for i in range(2):
        name_product = data.loc[i, "Nome"]
        url = 'https://www.netshoes.com.br/busca?nsCat=Natural&q=' + name_product
        navegador.get(url)
        waituntil(navegador, 'items-info')
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Quantidade de anuncios Netshoes
        try:
            container = site.find(class_="items-info")
            product_quantity_string = container.find('span', class_='block').getText()
            list_numbers_string = re.findall(r'\d+', product_quantity_string)
            results = list(map(int, list_numbers_string))
            product_quantity = results[-1]
            data.loc[i, 'Qnt_Netshoes'] = product_quantity
        except AttributeError:
            data.loc[i, 'Qnt_Netshoes'] = 0




def transformacao(data, name_list):
    global data_crescimento
    global data_desejada
    global data_popular

    # REORDENANDO COLUNAS
    data = data[['Posicao', 'Nome', 'Qnt_Normal', 'Qnt_FULL', 'Qnt_Netshoes', 'Link_ML', 'GoogleTrends', 'UltimaAtualizacao']]

    # CRIANDO 3 DATAFRAMES DIFERENTES
    data_crescimento = data.loc[data['Posicao'].str.contains('CRESCIMENTO')]
    data_desejada = data.loc[data['Posicao'].str.contains('DESEJADA')]
    data_popular = data.loc[data['Posicao'].str.contains('POPULAR')]

    # REMOVENDO STRING E CONVERTENDO POSICAO PARA INT
    data_crescimento['Posicao'] = data_crescimento['Posicao'].str.extract('(\d+)').astype(int)
    data_desejada['Posicao'] = data_desejada['Posicao'].str.extract('(\d+)').astype(int)
    data_popular['Posicao'] = data_popular['Posicao'].str.extract('(\d+)').astype(int)

    writer = pd.ExcelWriter('XLSX/' + name_list[l] + '-' + d1 + '.xlsx', engine='xlsxwriter')
    data_crescimento.to_excel(writer, sheet_name='Crescimento', index=False)
    data_desejada.to_excel(writer, sheet_name='Desejados', index=False)
    data_popular.to_excel(writer, sheet_name='Popular', index=False)

    for column in data_crescimento:
        column_length = max(data_crescimento[column].astype(str).map(len).max(), len(column))
        col_idx = data_crescimento.columns.get_loc(column)
        writer.sheets['Crescimento'].set_column(col_idx, col_idx, column_length)

    for column in data_desejada:
        column_length = max(data_desejada[column].astype(str).map(len).max(), len(column))
        col_idx = data_desejada.columns.get_loc(column)
        writer.sheets['Desejados'].set_column(col_idx, col_idx, column_length)

    for column in data_popular:
        column_length = max(data_popular[column].astype(str).map(len).max(), len(column))
        col_idx = data_popular.columns.get_loc(column)
        writer.sheets['Popular'].set_column(col_idx, col_idx, column_length)

    writer.save()


def bot_slack(name_list):
    # Settings
    env_path = Path('.') / 'C:\workspace\ProdutosTendencia\.env'
    load_dotenv(dotenv_path=env_path)
    app = slack.WebClient(token=os.environ['SLACK_TOKEN'])

    # # Seding
    # app.chat_postMessage(channel='produtos-tendencia-test', text="PRODUTOS TENDÊNCIAS - " + d1)
    app.files_upload(channels='produtos-tendencia-test', file='XLSX/' + name_list[l] + '-' + d1 + '.xlsx')


if __name__ == "__main__":
    url_list = ['https://tendencias.mercadolivre.com.br/1276-esportes_e_fitness',
                'https://tendencias.mercadolivre.com.br/1430-calcados__roupas_e_bolsas',
                'https://tendencias.mercadolivre.com.br/264586-saude']

    name_list = ['esportes_e_fitness', 'calcados__roupas_e_bolsas', 'saude']

    # Formating Date
    today = date.today()
    d1 = today.strftime("%d-%m-%Y")

    # Configurações Driver
    option = Options()
    option.headless = False
    navegador = webdriver.Firefox(options=option)
    navegador.maximize_window()

    # Disable Logs Pandas
    pd.set_option('mode.chained_assignment', None)

    # Mkdir
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    if not os.path.exists('XLSX'):
        os.makedirs('XLSX')

    # Call Functions
    for l in range(len(url_list)):
        pagina_tendencias(url_list)
        pagina_produtos(data)
        netshoes()
        transformacao(data, name_list)
        bot_slack(name_list)
