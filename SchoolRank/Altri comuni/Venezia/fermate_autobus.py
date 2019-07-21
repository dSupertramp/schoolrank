# coding: utf-8
import csv
import pandas as pd
import re
import numpy as np
import urllib
import requests
import time
import sys
import zipfile
import io


url = 'http://actv.avmspa.it/sites/default/files/attachments/opendata/navigazione/actv_nav.zip'
response = requests.get(url)
zf = zipfile.ZipFile(io.BytesIO(response.content))
try:
    trips = pd.read_csv(zf.open('trips.txt'))
    stops = pd.read_csv(zf.open('stops.txt'))
    stop_times = pd.read_csv(zf.open('stop_times.txt'))
except:
    trips = pd.read_csv(zf.open('trips.csv'))
    stops = pd.read_csv(zf.open('stops.csv'))
    stop_times = pd.read_csv(zf.open('stop_times.csv'))

df = pd.DataFrame()


trips = trips.applymap(str)
stops = stops.applymap(str)
stop_times = stop_times.applymap(str)

f = pd.merge(stops, stop_times, how='inner', on=['stop_id'])
f2 = pd.merge(trips, f, how='inner', on=['trip_id'])


df['IDVIAGGIO'] = f2['trip_id'].apply(
    lambda x: f2['trip_id'].str if x == f2['trip_id'].str else x)
df['IDFERMATA'] = f2['stop_id'].apply(
    lambda x: f2['stop_code'].str if x == f2['stop_id'].str else x)
df['LATITUDINEFERMATA'] = f2['stop_lat']
df['LONGITUDINEFERMATA'] = f2['stop_lon']
df['NOMEFERMATA'] = f2['stop_name']
df['NUMEROAUTOBUS'] = f2['route_id']


try:
    # 0 -> andata, 1 -> ritorno
    df['ANDATA'] = f2['direction_id']
    df['ANDATA'].replace('0', 'True', inplace=True)
    df['ANDATA'].replace('1', 'False', inplace=True)
except:
    pass

try:
    df = df.drop_duplicates(subset=['NOMEFERMATA', 'ANDATA'], keep='first')
except:
    df = df.drop_duplicates(subset=['NOMEFERMATA'], keep='first')


df.to_csv('Output_autobus.csv', index=False, encoding='utf-8')
