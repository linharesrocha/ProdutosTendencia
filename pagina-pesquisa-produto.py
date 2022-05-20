import statistics
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep

url = "https://lista.mercadolivre.com.br/bbs-airsoft"

# Configurações
option = Options()
option.headless = True
navegador = webdriver.Firefox(options=option)

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
#product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

# Container de Produtos
container = site.find(class_='ui-search-results')

# Produtos do Container
product_container = container.findAll('li', class_='ui-search-layout__item')

# Link de Cada produto
product_link = [p.find('a', href=True).get('href') for p in product_container]

products_price = []
products_quantity = []

# Acessa cada produto do Container da Categoria
products_length = len(product_link)
for i in range(products_length):
    print('{} / {}'.format(i, products_length))
    # Acessa página
    navegador.get(product_link[i])
    sleep(1)

    # Salva pagina
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    # Side bar Infos
    product_side_info = site.find(class_='pl-16')

    # Price
    price_fraction = product_side_info.find('span', class_ = 'andes-money-amount__fraction').getText()

    # Quantity
    quantity = product_side_info.find('span', class_ = 'ui-pdp-subtitle').getText()

    products_price.append(price_fraction)
    products_quantity.append(quantity)


# String p/ Int Price
products_price = list(map(int, products_price))




#
# # Redirecionando FULL
# navegador.get(url+"_Frete_Full")
#
# # Salvando a página
# page_content = navegador.page_source
# site = BeautifulSoup(page_content, 'html.parser')
#
# # Quantidade de anúncios FULL
# product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()