# coding: utf-8
import csv
import pandas as pd
import re
from geopy.geocoders import Nominatim
import numpy as np
import urllib
from contextlib import closing
import requests
import time
from timeit import default_timer as timer
import sys
import codecs


def cleaner(text):
    regex_dict = {
        r"N\.[0-9]{2}\/": r'',
        r'N\.[0-9]{1,2}': r'',
        r'N\.\s[0-9]{1,2}': r'',
        r'N\s[0-9]{1,2}': r'',
        r'[0-9]\/[A-Z]{1}': r'',
        r'([A-Z])(\d{1})': r'\1 \2',
    }

    replace_dict = {
        'P.ZZA': 'PIAZZA',
        'C.SO': 'CORSO',
        'snc': '',
        's.n.c': '',
        's.n.': '',
        'L.GO': 'LARGO',
        'PROLUNG.': 'PROLUNGAMENTO ',
                    '"': '',
                    'P.AZA': 'PIAZZA',
                    '-': ''
    }
    # keywords
    for key, values in replace_dict.items():
        text = text.replace(key, values)
    # regex
    for key in regex_dict:
        rx = re.compile(key)
        text = rx.sub(regex_dict[key], text)
    return text


# Estrazione
with open('Output_estrazione.csv', 'w', newline='') as csvoutput:
    output_fieldnames = ['NOMESCUOLA', 'DESCRIZIONECOMUNE', 'CODICESCUOLA', 'INDIRIZZO', 'LATITUDINE', 'LONGITUDINE',
                         'SITOWEB', 'DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA', 'CODICEISTITUTORIFERIMENTO', 'CAPSCUOLA']
    writer = csv.DictWriter(csvoutput, delimiter=',',
                            fieldnames=output_fieldnames)
    writer.writeheader()
    url = 'http://dati.istruzione.it/opendata/opendata/catalogo/elements1/leaf/SCUANAGRAFESTAT20181920180901.csv'
    response = urllib.request.urlopen(url)
    reader = csv.DictReader(codecs.iterdecode(response, 'utf-8'))
    geolocator = Nominatim(user_agent="my-application")
    comune = 'PALERMO'
    for row in reader:
        indirizzo = row['INDIRIZZOSCUOLA']
        indirizzo_pulito = cleaner(indirizzo)
        codice_istituto = row['CODICESCUOLA']
        descrizione_comune = row['DESCRIZIONECOMUNE']
        nome_scuola = row['DENOMINAZIONEISTITUTORIFERIMENTO']
        sito_web = row['SITOWEBSCUOLA']
        tipologia_scuola = row['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA']
        codice_istituto_riferimento = row['CODICEISTITUTORIFERIMENTO']
        cap_scuola = row['CAPSCUOLA']
        indirizzo_pulito_cap = indirizzo_pulito+' '+row['CAPSCUOLA']
        if str(comune) == str(descrizione_comune).upper():
            try:
                start = timer()
                location = geolocator.geocode(indirizzo_pulito_cap)
                latitude = location.latitude
                longitude = location.longitude
                end = timer()
                print(end-start)
            except:
                latitude = None
                longitude = None
            # Scrittura
            output_row = {}
            output_row['NOMESCUOLA'] = nome_scuola
            output_row['DESCRIZIONECOMUNE'] = descrizione_comune.upper()
            output_row['CODICESCUOLA'] = codice_istituto
            output_row['INDIRIZZO'] = indirizzo_pulito.upper()
            output_row['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA'] = tipologia_scuola
            output_row['LATITUDINE'] = latitude
            output_row['LONGITUDINE'] = longitude
            if 'non' in sito_web.lower():
                output_row['SITOWEB'] = None
            else:
                output_row['SITOWEB'] = 'http://'+sito_web.lower()
            output_row['CODICEISTITUTORIFERIMENTO'] = codice_istituto_riferimento
            output_row['CAPSCUOLA'] = cap_scuola
            writer.writerow(output_row)


df = pd.read_csv('Output_estrazione.csv')
df.dropna(subset=['LATITUDINE'], how='all', inplace=True)
df.to_csv('Output_estrazione.csv', index=False)

