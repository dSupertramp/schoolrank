# coding: utf-8
import urllib
import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, OWL, XSD, DC, DCTERMS
import requests
import re
from geopy.distance import geodesic
from SPARQLWrapper import SPARQLWrapper, JSON


g = Graph()
g.parse('Dataset_finale.ttl', format='turtle')
skr = Namespace("http://www.schoolrank.org/ontology/")
schema = Namespace('https://schema.org/')
base_uri = "http://www.schoolrank.org/resource/"
g.bind("skr", skr)
g.bind('schema', schema)


qres = g.query(
    # Insert query
    '''
SELECT count(*) as ?numero_scuole_e_plessi
WHERE{
    ?scuole skr:comune ?nome_scuola.
}

    '''
)

print("\n=============================================================QUERY RESULTS================================================================\n")

for row in qres:
    print(row['numero_scuole_e_plessi'], "\t")
