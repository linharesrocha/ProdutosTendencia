import sqlite3
import pandas as pd
from sqlalchemy import create_engine


def start_sqlite():
    db = create_engine('sqlite:///SQL/db_tendencias_ml.sqlite', echo=False)
    conn = db.connect()

    # dataset
    df_crescimento = pd.read_csv('CSV/produtos_crescimento.csv')
    df_desejado = pd.read_csv('CSV/produtos_desejado.csv')
    df_popular = pd.read_csv('CSV/produtos_popular.csv')

    schema_crescimento = """
    CREATE TABLE crescimento(
      Posicao INTEGER,
      Nome TEXT,
      Qnt_Normal INTEGER,
      Qnt_FULL INTEGER,
      Media_Preco REAL,
      Mediana_Preco INTEGER,
      Media_Vendas INTEGER,
      Mediana_Vendas INTEGER,
      Link TEXT,
      GoogleTrends TEXT,
      scrapy_datetime TEXT
      )
      """

    schema_desejado = """
    CREATE TABLE desejado(
      Posicao INTEGER,
      Nome TEXT,
      Qnt_Normal INTEGER,
      Qnt_FULL INTEGER,
      Media_Preco REAL,
      Mediana_Preco INTEGER,
      Media_Vendas INTEGER,
      Mediana_Vendas INTEGER,
      Link TEXT,
      GoogleTrends TEXT,
      scrapy_datetime TEXT
      )
      """

    schema_popular = """
    CREATE TABLE popular(
      Posicao INTEGER,
      Nome TEXT,
      Qnt_Normal INTEGER,
      Qnt_FULL INTEGER,
      Media_Preco REAL,
      Mediana_Preco INTEGER,
      Media_Vendas INTEGER,
      Mediana_Vendas INTEGER,
      Link TEXT,
      GoogleTrends TEXT,
      scrapy_datetime TEXT
      )
      """

    try:
        conn.execute(schema_crescimento)
        conn.execute(schema_desejado)
        conn.execute(schema_popular)
    except:
        print('Schema ja criado')


    # Insert data into table
    df_crescimento.to_sql('crescimento', con=conn, if_exists='replace', index=False)
    df_desejado.to_sql('desejado', con=conn, if_exists='replace', index=False)
    df_popular.to_sql('popular', con=conn, if_exists='replace', index=False)

    conn.close()