# Imports
import slack
import os
from pathlib import Path
from dotenv import load_dotenv

def bot_slack():
    # Settings
    env_path = Path('.') / 'Slack/.env'
    load_dotenv(dotenv_path=env_path)
    app = slack.WebClient(token=os.environ['SLACK_TOKEN'])

    # Seding
    app.chat_postMessage(channel='trends', text="PRODUTOS TENDÊNCIAS!")
    app.files_upload(channels='trends', file='XLSX/esporte_e_fitness.xlsx')
