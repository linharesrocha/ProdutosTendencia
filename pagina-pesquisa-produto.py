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

for i in range(1, 30):
    body.send_keys(Keys.PAGE_DOWN)
sleep(4)

# Salvando a página
page_content = navegador.page_source
site = BeautifulSoup(page_content, 'html.parser')

# Quantidade de anúncios normal
product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()

# Container de Produtos
container = site.find(class_='ui-search-results')

# Produtos do Container
product_container = container.findAll('li', class_='ui-search-layout__item')

# Link de Cada produto
product_link = [p.find('a', href=True).get('href') for p in product_container]

products_price = []
products_quantity = []

# Acessa cada produto do Container da Categoria
for i in range(len(product_link)):
    print("=" * 10)
    print(i)
    # Acessa página
    navegador.get(product_link[i])
    print(navegador.current_url)
    sleep(2)

    # Salva pagina
    page_content = navegador.page_source
    site = BeautifulSoup(page_content, 'html.parser')

    # Side bar Infos
    product_side_info = site.find(class_='pl-16')

    # Price
    price_fraction = product_side_info.find('span', class_ = 'andes-money-amount__fraction').getText()
    print(price_fraction)

    # Quantity
    quantity = product_side_info('span', class_ = 'ui-pdp-subtitle').getText()
    print(quantity)

    products_price.append(price_fraction)
    products_quantity.append(quantity)

print(products_price)
print(products_quantity)
print("mean" * 10 )
print('price')
print(statistics.mean(products_price))
print('quantity')
print(statistics.mean((products_quantity)))
print("median" * 10 )
print('price')
print(statistics.median(products_price))
print('quantity')
print(statistics.median((products_quantity)))









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