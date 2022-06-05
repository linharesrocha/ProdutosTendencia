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
        print('Classe nao encontrada ' + class_)


def down_page(body):
    for i in range(1, 20):
        body.send_keys(Keys.PAGE_DOWN)


def posicao_nomes_links():
    global data

    url = 'https://tendencias.mercadolivre.com.br/1276-esportes_e_fitness'

    # Iniciando Navegador
    navegador.get(url)

    # Descendo a pagina para carregar todos os produtos
    body = navegador.find_element(By.CSS_SELECTOR, "body")

    down_page(body)

    waituntil(navegador, 'ui-search-entry-keyword')
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    page_trends = site.findAll(class_="ui-search-carousel")

    # Criando lista para armazenar produtos dos 3 Carroseis
    posicao = []
    nome = []
    link = []

    # Todas as categorias: Cresceram/Deseajados/Populares
    for categoria in range(len(page_trends)):

        # Pegando todos os cards do carrousel de produtos
        category_trends = page_trends[categoria].findAll('div', class_='entry-column')

        for product in category_trends:
            posicao.append(product.find('div', class_='ui-search-entry-description').getText())
            nome.append(product.find('h3', class_='ui-search-entry-keyword').getText())
            link.append(product.find('a', href=True).get('href').replace('#trend', ''))

    dicionario = {'Posicao': posicao, 'Nome': nome, 'Link_ML': link}
    data = pd.DataFrame(dicionario)

    return data


def qntd_nomal_e_full(data):
    list_links_ml = data['Link_ML'].tolist()

    normal_quantity = []
    full_quantity = []

    # Acessa cada produto
    for link in list_links_ml:
        navegador.get(link)

        waituntil(navegador, 'ui-search-search-result__quantity-results')
        page_content = navegador.page_source
        site = BeautifulSoup(page_content, 'html.parser')

        # Quantidade de anúncios na modalidade envio normal
        normal_string_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
        normal_int_quantity = int(re.sub('[^0-9]', '', normal_string_quantity))

        # Quantidade de anúncios na modalidade de envio Full
        try:
            navegador.get(link + "_Frete_Full")
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')
            full_string_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
            full_int_quantity = int(re.sub('[^0-9]', '', full_string_quantity))
        except AttributeError:
            full_int_quantity = 0

        normal_quantity.append(normal_int_quantity)
        full_quantity.append(full_int_quantity)

    data['Qnt_ML'] = normal_quantity
    data['Qnt_FULL'] = full_quantity

    return data


def google_trends(data):
    # Lista dos nomes dos produtos
    list_product_names = data['Nome'].tolist()

    url_google_trends = "https://trends.google.com.br/trends/explore?geo=BR&q="
    linkTrends = []

    for name in list_product_names:
        linkTrends.append(url_google_trends + name)

    data['GoogleTrends'] = linkTrends

    return data


def qntd_netshoes(data):
    list_qntd_netshoes = []

    # Lista dos nomes dos produtos
    list_product_names = data['Nome'].tolist()
    url = 'https://www.netshoes.com.br/busca?nsCat=Natural&q='

    for name in list_product_names:
        navegador.get(url + name)
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
        except AttributeError:
            product_quantity = 0

        list_qntd_netshoes.append(product_quantity)

    data['Qnt_Netshoes'] = list_qntd_netshoes

    return data


def ultima_atualizacao(data):
    data['UltimaAtualizacao'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    return data


def salvando_excel(data):

    # REORDENANDO COLUNAS
    data = data[['Posicao', 'Nome', 'Qnt_ML', 'Qnt_FULL', 'Qnt_Netshoes',
                 'Link_ML', 'GoogleTrends', 'UltimaAtualizacao']]

    writer = pd.ExcelWriter('XLSX/' + 'Tendencias' + '-' + d1 + '.xlsx', engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Tendencias', index=False)

    for column in data:
        column_length = max(data[column].astype(str).map(len).max(), len(column))
        col_idx = data.columns.get_loc(column)
        writer.sheets['Tendencias'].set_column(col_idx, col_idx, column_length)

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
    option.headless = True
    navegador = webdriver.Firefox(options=option)
    navegador.maximize_window()

    # Disable Logs Pandas
    # pd.set_option('mode.chained_assignment', None)

    # Mkdir
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    if not os.path.exists('XLSX'):
        os.makedirs('XLSX')

    # Call Functions
    posicao_nomes_links()
    qntd_nomal_e_full(data)
    google_trends(data)
    qntd_netshoes(data)
    ultima_atualizacao(data)
    salvando_excel(data)
    # bot_slack(name_list)
