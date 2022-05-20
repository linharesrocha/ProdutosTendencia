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

# Pegando quantidade de anúncios no normal
product_normal_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
print(product_normal_quantity)

# Redirecionando a página
navegador.get(url+"_Frete_Full")

# Salvando a página novamente
page_content = navegador.page_source
site = BeautifulSoup(page_content, 'html.parser')

# Pegando quantidade de anúncios no full
product_full_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
print(product_full_quantity)