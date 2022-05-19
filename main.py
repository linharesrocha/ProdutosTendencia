from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep


url = "https://tendencias.mercadolivre.com.br/1276-esportes_e_fitness"

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


# Carrousel -> As buscas que mais cresceram
carrousel_grow = site.find(class_="ui-search-carousel")

# Pegando produtos -> As buscas que mais cresceram
product_list = carrousel_grow.findAll('div', class_='entry-column')

product_name_grow = [p.find('p', class_ = 'ui-search-entry-keyword').getText() for p in product_list]
print(product_name_grow)
