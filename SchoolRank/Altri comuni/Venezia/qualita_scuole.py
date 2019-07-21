# coding: utf-8
import csv
import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import numpy as np
from contextlib import closing
import requests
import time
import sys


df1 = pd.DataFrame()
df2 = pd.DataFrame()
df3 = pd.DataFrame()
# la sigla identifica direttamente il comune, eliminando le provincie
# es: PA indica tutte le scuole appartenenti a Palermo come citta
sigla = 'VE'

ambiente = pd.read_csv(
    'http://dati.istruzione.it/opendata/opendata/catalogo/elements1/leaf/EDIAMBFUNZSTA20171820180925.csv')
barriera = pd.read_csv(
    'http://dati.istruzione.it/opendata/EDISUPBARARCSTA20171820180925.csv')
riscaldamento = pd.read_csv(
    'http://dati.istruzione.it/opendata/EDITIPORISCSTA20171820180925.csv')

ambiente = ambiente.sort_values(by=['CODICESCUOLA'])
riscaldamento = riscaldamento.sort_values(by=['CODICESCUOLA'])
barriera = barriera.sort_values(by=['CODICESCUOLA'])


# Ambienti
df1['CODICESCUOLA'] = ambiente['CODICESCUOLA']
df1['CODICEEDIFICIO'] = ambiente['CODICEEDIFICIO']
df1['SPAZIDIDATTICI'] = ambiente['SPAZIDIDATTICI']
df1['AULAMAGNA'] = ambiente['AULAMAGNA']
df1['MENSA'] = ambiente['MENSA']
df1['PALESTRAPISCINA'] = ambiente['PALESTRAPISCINA']
df1['SPAZIAMMINISTRATIVI'] = ambiente['SPAZIAMMINISTRATIVI']

# Barriere
df2['CODICESCUOLA'] = barriera['CODICESCUOLA']
df2['CODICEEDIFICIO'] = barriera['CODICEEDIFICIO']
df2['SUPERAMENTOBARRIEREARCH'] = barriera['SUPERAMENTOBARRIEREARCH']
df2['ACCESSORAMPE'] = barriera['ACCESSORAMPE']
df2['SCALENORMA'] = barriera['SCALENORMA']
df2['ASCENSOREDISABILI'] = barriera['ASCENSOREDISABILI']
df2['PIATTAFORMAELEVATRICE'] = barriera['PIATTAFORMAELEVATRICE']
df2['SERVIZIIGIENICIDISABILI'] = barriera['SERVIZIIGIENICIDISABILI']
df2['PORTELARGHEZZADISABILI'] = barriera['PORTELARGHEZZADISABILI']
df2['PERCORSIINTERNIDISABILI'] = barriera['PERCORSIINTERNIDISABILI']
df2['PERCORSIESTERNIDISABILI'] = barriera['PERCORSIESTERNIDISABILI']
df2['ALTRIACCORGIMENTIDISABILI'] = barriera['ALTRIACCORGIMENTIDISABILI']

# Riscaldamento
df3['CODICESCUOLA'] = riscaldamento['CODICESCUOLA']
df3['CODICEEDIFICIO'] = riscaldamento['CODICEEDIFICIO']
df3['IMPIANTORISCALDAMENTO'] = riscaldamento['IMPIANTORISCALDAMENTO']
df3['CENTRALIZZATOOLIOCOMBUSTIBILI'] = riscaldamento['CENTRALIZZATOOLIOCOMBUSTIBILI']
df3['CENTRALIZZATOGASOLIO'] = riscaldamento['CENTRALIZZATOGASOLIO']
df3['CENTRALIZZATOMETANO'] = riscaldamento['CENTRALIZZATOMETANO']
df3['CENTRALIZZATOGPL'] = riscaldamento['CENTRALIZZATOGPL']
df3['CENTRALIZZATOARIA'] = riscaldamento['CENTRALIZZATOARIA']
df3['CORPISCALDANTIELETTRICIAUTONOMI'] = riscaldamento['CORPISCALDANTIELETTRICIAUTONOMI']
df3['TELERISCALDAMENTO'] = riscaldamento['TELERISCALDAMENTO']
df3['CONDIZIONAMENTOVENTILAZIONE'] = riscaldamento['CONDIZIONAMENTOVENTILAZIONE']
df3['RISCALDAMENTOALTRANATURA'] = riscaldamento['RISCALDAMENTOALTRANATURA']


# Ambienti
df1 = df1.replace({'-': 'False'}, regex=True)
df1 = df1.replace({'Non Comunicato': 'False'}, regex=True)
df1 = df1.replace({'Non Esiste': 'False'}, regex=True)
df1 = df1.replace({'Esiste': 'True'}, regex=True)
df1 = df1.replace({'SI': 'True'}, regex=True)
df1 = df1.replace({'NO': 'False'}, regex=True)

# Barriere
df2 = df2.replace({'SI': 'True'}, regex=True)
df2 = df2.replace({'NO': 'False'}, regex=True)
df2 = df2.replace({'-': 'False'}, regex=True)

# Riscaldamento
df3 = df3.replace({'SI': 'True'}, regex=True)
df3 = df3.replace({'NO': 'False'}, regex=True)
df3 = df3.replace({'-': 'False'}, regex=True)


df2['ALTRIACCORGIMENTIDISABILI'] = df2['ALTRIACCORGIMENTIDISABILI'].replace({
                                                                            ' ': ''}, regex=True)
df3['RISCALDAMENTOALTRANATURA'] = df3['RISCALDAMENTOALTRANATURA'].replace({
                                                                          ' ': ''}, regex=True)
df2['ALTRIACCORGIMENTIDISABILI'] = df2['ALTRIACCORGIMENTIDISABILI'].replace(
    {'[^a-zA-Z0-9]': ''}, regex=True)
df3['RISCALDAMENTOALTRANATURA'] = df3['RISCALDAMENTOALTRANATURA'].replace(
    {'[^a-zA-Z0-9]': ''}, regex=True)
df2['ALTRIACCORGIMENTIDISABILI'] = df2['ALTRIACCORGIMENTIDISABILI'].replace(
    {'\w+': 'True'}, regex=True)
df3['RISCALDAMENTOALTRANATURA'] = df3['RISCALDAMENTOALTRANATURA'].replace(
    {'\w+': 'True'}, regex=True)


df1.to_csv('Output_ambiente.csv', index=False)
df2.to_csv('Output_barriere.csv', index=False)
df3.to_csv('Output_riscaldamento.csv', index=False)


s1 = pd.merge(df1, df2, how='inner', on=['CODICESCUOLA', 'CODICEEDIFICIO'])
s2 = pd.merge(s1, df3, how='inner', on=['CODICESCUOLA', 'CODICEEDIFICIO'])
s2 = s2.sort_values(by=['CODICESCUOLA'])

# Elimina tutte le scuole che non sono di Palermo
s2 = s2.loc[s2['CODICESCUOLA'].str.contains(r'^'+sigla+r'\w+')]


# prende tutti i campi necessari tranne quello del codice scuola, che non serve
num_elementi = len(s2.columns)
num_elementi -= 2

# il rank e' ottenuto da:
# Il numero di ogni servizio presente in una riga diviso il suo numero totale. Si arriva cosi ad un numero compreso tra 1 a 10
s2['RANK'] = (s2.iloc[:, 2:] == 'True').sum(axis=1)/num_elementi*10
# round del rank
s2['RANK'] = s2['RANK'].apply(lambda x: round(x, 2))


s2.to_csv('Output_rank.csv', index=False)
