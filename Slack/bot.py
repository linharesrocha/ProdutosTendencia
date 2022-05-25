# Imports
from datetime import date
import slack
import os
from pathlib import Path
from dotenv import load_dotenv

def bot_slack():
    # Settings
    env_path = Path('.') / 'C:\workspace\ProdutosTendencia\Slack\.env'
    load_dotenv(dotenv_path=env_path)
    app = slack.WebClient(token=os.environ['SLACK_TOKEN'])

    # Formating Date
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    # Seding
    for i in range(0, 5):
        app.chat_postMessage(channel='trends', text=" ")
    app.chat_postMessage(channel='trends', text="PRODUTOS TENDÊNCIAS - " + d1)
    app.files_upload(channels='trends', file='XLSX/esporte_e_fitness.xlsx')
