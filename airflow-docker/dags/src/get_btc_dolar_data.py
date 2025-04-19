#%pip install requests
#%pip install pandas
#%pip install beautifulsoup4
#%pip install psycopg2
#%pip install sqlalchemy
# import sys
# import subprocess


# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'beautifulsoup4'])
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2'])
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'sqlalchemy'])

import requests
import json
import pandas as pd
from datetime import datetime
import urllib.request
import time
from bs4 import BeautifulSoup
from decimal import Decimal
import numpy as np
import psycopg2
from io import StringIO
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine

def format_date(data_str):
    try:
        date_format = '%d/%m/%Y'
        return datetime.strptime(data_str, date_format)
    except:
        return datetime.strptime("01/01/1970", date_format)
    

def format_date2(date_str):
    date_format = '%b %d, %Y'
    return datetime.strptime(date_str, date_format)


def write_df_to_table_without_index(df, table_name, schema_name, engine):
    """
    Truncate existing table and load df into table.
    Keep each column as string to avoid datatype conflicts.
    """
    df.head(0).to_sql(table_name, engine, if_exists='replace',schema=schema_name, index=False)

    conn = engine.raw_connection()
    cur = conn.cursor()
    output = StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_expert(f"COPY {schema_name}.{table_name} FROM STDIN", output)
    conn.commit()

#docker run -p 5432:5432 -d -e POSTGRES_PASSWORD=1234 postgres
# engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')
engine = create_engine('postgresql://postgres:1234@host.docker.internal:5432/postgres')


def write_df_to_table_without_index(df, table_name, schema_name, engine):
    """
    Truncate existing table and load df into table.
    Keep each column as string to avoid datatype conflicts.
    """
    df.head(0).to_sql(table_name, engine, if_exists='replace',schema=schema_name, index=False)

    conn = engine.raw_connection()
    cur = conn.cursor()
    output = StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_expert(f"COPY {schema_name}.{table_name} FROM STDIN", output)
    conn.commit()
#SERIE HISTORICA DO DOLAR

req = urllib.request.Request('https://www.cepea.esalq.usp.br/br/serie-de-preco/dolar.aspx?todos=true', headers={'User-Agent' : "Magic Browser"}) 
#file = urllib.request.urlopen( req )
#print(con.read())

colnames=['data','cotacao_dolar'] 
with urllib.request.urlopen(req) as f:
#    file = f.read()
    df_historico_dolar = pd.read_csv(f, sep='\t', lineterminator='\n', encoding='latin-1', names=colnames, skiprows=1)

#SERIE HISTORICA DO DOLAR - BACKUP
#df_historico_dolar = pd.read_csv("../data/export_series_dolar.xls", sep='\t', lineterminator='\n', encoding='latin-1', names=colnames, skiprows=1)

df_historico_dolar['data'] = df_historico_dolar['data'].apply(format_date).astype(str)


#SERIE HISTORICA DO CDI
req = urllib.request.Request('https://www.cepea.esalq.usp.br/br/serie-de-preco/cdi.aspx?todos=truee', headers={'User-Agent' : "Magic Browser"}) 

colnames=['data','cdi'] 
with urllib.request.urlopen(req) as f:
    df_historico_cdi = pd.read_csv(f, sep='\t', lineterminator='\n', encoding='latin-1', names=colnames, skiprows=1)

#SERIE HISTORICA DO CDI - BACKUP
#df_historico_cdi = pd.read_csv("../data/export_series_cdi.xls", sep='\t', lineterminator='\n', encoding='latin-1', names=colnames, skiprows=1)

df_historico_cdi['data'] = df_historico_cdi['data'].apply(format_date).astype(str)
df_historico_cdi["data"] = pd.to_datetime(df_historico_cdi["data"])
df_historico_cdi["cdi"] = df_historico_cdi["cdi"].str.replace("%", "")
df_historico_cdi["cdi"] = df_historico_cdi["cdi"].str.replace(",", ".")
df_historico_cdi["cdi"] = df_historico_cdi["cdi"].astype(float)

#HISTORICO DE COTACOES BTC - USD
period1 = 1410912000  # Início (2014-09-17)
period2 = int(time.time())  # Fim (hoje)

# URL da API de histórico do Yahoo Finance (formato CSV)
url = f"https://finance.yahoo.com/quote/BTC-USD/history/?period1={period1}&period2={period2}"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Procura por linhas da tabela de histórico
rows = soup.find_all("tr", attrs={"class": "yf-1jecxey"})

df_historico_btc = pd.DataFrame(columns=["data", "abertura", "alta", "baixa", "fechamento", "ajuste_fechamento", "volume"])
for row in rows[1:]:
    cols = row.find_all("td")
    data = [col.text for col in cols]
    #df_historico_btc = df_historico_btc.concat({"data": data[0], "abertura": data[1], "alta": data[2], "baixa": data[3], "fechamento": data[4], "ajuste_fechamento": data[5], "volume": data[6]}, ignore_index=True)
    df_historico_btc = pd.concat([pd.DataFrame([[data[0],data[1],data[2],data[3],data[4],data[5],data[6]]], columns=df_historico_btc.columns), df_historico_btc], ignore_index=True)


df_historico_btc['data'] = df_historico_btc['data'].apply(format_date2).astype(str)

df_btc_dolar = pd.merge(df_historico_btc, df_historico_dolar, on="data", how="inner")

df_btc_dolar["cotacao_dolar"] = df_btc_dolar["cotacao_dolar"].str.replace(",", ".")
df_btc_dolar["ajuste_fechamento"] = df_btc_dolar["ajuste_fechamento"].str.replace(",", "")
df_btc_dolar["abertura"] = df_btc_dolar["abertura"].str.replace(",", "")
df_btc_dolar["alta"] = df_btc_dolar["alta"].str.replace(",", "")
df_btc_dolar["baixa"] = df_btc_dolar["baixa"].str.replace(",", "")
df_btc_dolar["fechamento"] = df_btc_dolar["fechamento"].str.replace(",", "")
df_btc_dolar["volume"] = df_btc_dolar["volume"].str.replace(",", "")

df_btc_dolar["cotacao_dolar"] = df_btc_dolar["cotacao_dolar"].astype(float)
df_btc_dolar["ajuste_fechamento"] = df_btc_dolar["ajuste_fechamento"].astype(float)
df_btc_dolar["abertura"] = df_btc_dolar["abertura"].astype(float)
df_btc_dolar["alta"] = df_btc_dolar["alta"].astype(float)
df_btc_dolar["baixa"] = df_btc_dolar["baixa"].astype(float)
df_btc_dolar["fechamento"] = df_btc_dolar["fechamento"].astype(float)
df_btc_dolar["volume"] = df_btc_dolar["volume"].astype(float)
df_btc_dolar["data_str"] = df_btc_dolar["data"]
df_btc_dolar["data"] = pd.to_datetime(df_btc_dolar["data"])
# df_btc_dolar["data_mes_ano"] = df_btc_dolar.apply(lambda row: (row['data'].strftime('%B-%Y')), axis=1)
df_btc_dolar["data_mes"] = df_btc_dolar.apply(lambda row: (row['data'].strftime('%m')), axis=1).astype(int)
df_btc_dolar["data_ano"] =  df_btc_dolar.apply(lambda row: (row['data'].strftime('%Y')), axis=1).astype(int)

df_btc_dolar['cotacao_btc_real'] = df_btc_dolar.apply(lambda row: round((row['cotacao_dolar'] * row['ajuste_fechamento']),2), axis=1)

#df_btc_dolar.tail(100)

write_df_to_table_without_index(df_btc_dolar, "historico_cotacoes_btc", "public", engine)
write_df_to_table_without_index(df_historico_cdi, "historico_cdi", "public", engine)   
