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


rank = pd.read_csv('Output_rank.csv')
estrazione = pd.read_csv('Output_estrazione.csv')
f = pd.DataFrame()
# merge dei 2 dataframe prendendo come chiavi CODICESCUOLA da rank e CODICEISTITUTODIRIFERIMENTO da estrazione
f = pd.merge(rank, estrazione, how='inner', left_on='CODICESCUOLA',
             right_on='CODICEISTITUTORIFERIMENTO')

# faccio il drop delle colonne obsolete
f = f.drop(['CODICESCUOLA_x', 'CODICEEDIFICIO'], axis=1)
# drop delle righe con campo indirizzo null
f.dropna(subset=['INDIRIZZO'], how='all', inplace=True)
# drop dei duplicati di CODISCUOLA che apparteneva a estrazione
f = f.drop_duplicates(['CODICESCUOLA_y'], keep='first')
# rinomino la colonna
f.rename(columns={'CODICESCUOLA_y': 'CODICESCUOLA'}, inplace=True)

f.to_csv('Output_finale.csv', index=False)
