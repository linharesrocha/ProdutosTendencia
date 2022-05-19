# TESTE
# TESTE
# TESTE
# TESTE
# TESTE
# TESTE

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
option.headless = False # true esconde
navegador = webdriver.Firefox(options=option)

# Iniciando Navegador
navegador.get(url)

# Descendo a pagina para carregar todos os produtos
body = navegador.find_element(By.CSS_SELECTOR, "body")

# Salvando a página
page_content = navegador.page_source
site = BeautifulSoup(page_content, 'html.parser')

# Pegando produtos -> As buscas que mais cresceram
product_list = site.findAll(class_="ui-search-carousel:nth-child(1)")
print(len(product_list))


# for p in product_list:
#     print(p.find('p', {'class': 'ui-search-carousel:nth-child(1) ui-search-entry-keyword'}))


# .ui-search-carousel:nth-child(1) .andes-card--padding-0