import urllib
import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, OWL, XSD, DC, DCTERMS
import requests
import re
from geopy.distance import geodesic


#skr = schoolrank

g = Graph()
skr = Namespace("http://www.schoolrank.org/ontology/")
schema = Namespace('https://schema.org/')
base_uri = "http://www.schoolrank.org/resource/"
g.bind("skr", skr)
g.bind('schema', schema)


def urify_fermata(nomefermata):
    replace_dict = {
        ' - ':' ',
        " ": "_",
        "'": '_',
        ".": '',
        '"': '',
        '__':'_'
    }
    regex_dict = {

    }
    # replace
    for key, values in replace_dict.items():
        nomefermata = nomefermata.replace(key, values)
    # regex
    for key in regex_dict:
        rx = re.compile(key)
        nomefermata = rx.sub(regex_dict[key], nomefermata)
    return nomefermata


# Ontologia trasporti
with open('Output_autobus.csv') as csvfile:
    reader_autobus = csv.DictReader(csvfile)
    for row in reader_autobus:
        uri_point = base_uri+"point/"+urify_fermata((row['NOMEFERMATA']))
        uri_autobus = base_uri+str(row['IDFERMATA'])
        g.add([URIRef(uri_autobus), RDF.type, skr.Autobus])
        # data properties
        g.add([URIRef(uri_autobus), skr.nomeFermata, Literal(
            row['NOMEFERMATA'], datatype=XSD.string)])
        g.add([URIRef(uri_autobus), skr.numeroAutobus, Literal(
            row['NUMEROAUTOBUS'], datatype=XSD.string)])
        try:
            g.add([URIRef(uri_autobus), skr.andata, Literal(
                row['ANDATA'], datatype=XSD.boolean)])
        except:
            pass
        g.add([URIRef(uri_point), schema.latitude,
               Literal(row['LATITUDINEFERMATA'])])
        g.add([URIRef(uri_point), schema.longitude,
               Literal(row['LONGITUDINEFERMATA'])])

        # object properties
        g.add([URIRef(uri_autobus), skr.coordinate, URIRef(uri_point)])
        g.add([URIRef(uri_point), RDF.type, schema.GeoCoordinates])


def urify_indirizzo(indirizzo):
    replace_dict = {
        " ":"_",
        ".":'_',
        "'":"_",
        '__':'_'
    }
    regex_dict ={
        r'[_]*$' : '',
    }
    #replace
    for key, values in replace_dict.items():
        indirizzo = indirizzo.replace(key, values)
    #regex
    for key in regex_dict:
        rx = re.compile(key)
        indirizzo = rx.sub(regex_dict[key], indirizzo)
    return indirizzo


def urify_scuola(nomescuola):
    replace_dict ={
        "I. FLORIO - S. LORENZO":"IGNAZIO FLORIO SAN LORENZO",
        "E. ARCULEO":"ETTORE ARCULEO",
        "F. SAVERIO CAVALLARI":"FRANCESCO SAVERIO CAVALLARI",
        "A. DE GASPERI":"ALCIDE DE GASPERI",
        "E. DE AMICIS":"EDMONDO DE AMICIS",
        "A. GABELLI":"ARISTIDE GABELLI",
        "N. GARZILLI":"NICOLO GARZILLI",
        "E. SALGARI":"EMILIO SALGARI",
        "F. ORESTANO":"FRANCESCO ORESTANO",
        "C. MANERI":"CARMELO MANERI",
        "M.TERESA DI CALCUTTA":"MADRE TERESA DI CALCUTTA",
        "G.A.COLOZZA":"GIOVANNI ANTONIO COLOZZA",
        "G. DI VITTORIO":"GIUSEPPE DI VITTORIO",
        "TOMASI DI L.":"TOMASI DI LAMPEDUSA",
        "G. E. NUCCIO":"GIUSEPPE ERNESTO NUCCIO",
        "L.DA VINCI /G.CARDUCCI":"LEONARDO DA VINCI GIOSUE CARDUCCI",
        "M.RAPISARDI":"MARIO RAPISARDI",
        "R. SANZIO":"RAFFAELLO SANZIO",
        "E. MEDI":"ENRICO MEDI",
        "A. VOLTA":"ALESSANDRO VOLTA",
        "E ASCIONE":"ERNESTO ASCIONE",
        "L.EINAUDI":"LUIGI EINAUDI",
        "CESAREO G.A.":"CESAREO GIOVANNI ALFREDO",
        "V.E. ORLANDO":"VITTORIO EMANUELE ORLANDO",
        "D. DOLCI":"DANILO DOLCI",
        "L.PIRANDELLO/B. ULIVIA":"LUIGI PIRANDELLO BORGO ULIVIA",
        "S.D'ACQUISTO BAGHERIA":"SALVO D' ACQUISTO BAGHERIA",
        'I.C. ':'','I.C.':'','- PA':'','-PA':'','D.D. ':'','I.C.S ':'','I.I.S. ':'','I.P.S.S.E.O.A. ':'','ITI ':'','LICEO ARTISTICO STATALE ':'',' (EX III ALBERGH)':'',
        'LICEO SCIENZE UMANE E LING. ':'','IM ':'','CPIA ':'','SCUOLA SEC. DI 1? ':'','SMS ':'','S.M.S. ':'','I.C PRINCIP. ':'','"':'',
        '" ':'','I.I.S.S. ':'',"__":"_"," _":"_"," /":"_",'/':'_',' / ':'_'," 1":"","'":"","IS MAJORANA":"MAJORANA","BORGESE-":"BORGESE_",
        " MATTARELLA -BONAGIA":"MATTARELLA BONAGIA",'SPERONE_ ':'SPERONE_',' GIOENI - ':'GIOENI_','RUSSO_ ':'RUSSO_','PEREZ-':'PEREZ_','. ':'.'
    }

    regex_dict={
        r'[ ]*$' : '',
    }

    #replace
    for key, values in replace_dict.items():
        nomescuola = nomescuola.replace(key, values)
    #regex
    for key in regex_dict:
        rx = re.compile(key)
        nomescuola = rx.sub(regex_dict[key],nomescuola)
    return nomescuola


#Ontologia scuola e plesso
with open('Output_finale.csv') as csvfile:
    reader_scuola = csv.DictReader(csvfile)
    for row in reader_scuola:
        uri_scuola=base_uri+str(row['CODICEISTITUTORIFERIMENTO'])
        uri_point = base_uri+"point/"+urify_indirizzo(row['INDIRIZZO'])
        uri_plesso=base_uri+str(row['CODICESCUOLA'])
        #Scuola
        if(row['CODICESCUOLA'] == row['CODICEISTITUTORIFERIMENTO']):
            g.add([URIRef(uri_scuola), RDF.type, skr.Scuola])
            #data properties
            g.add([URIRef(uri_scuola), skr.valutazione, Literal(row['RANK'], datatype=XSD.float)])
            g.add([URIRef(uri_scuola), skr.haCodiceIstitutoRiferimento, Literal(row['CODICEISTITUTORIFERIMENTO'],datatype=XSD.string)])
            g.add([URIRef(uri_scuola), skr.haDescrizioneTipologiaGradoIstruzioneScuola, Literal(row['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haAccessoRampe, Literal(row['ACCESSORAMPE'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haAltriAccorgimentiDisabili, Literal(row['ALTRIACCORGIMENTIDISABILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haSpaziDidattici, Literal(row['SPAZIDIDATTICI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haSpaziAmministrativi, Literal(row['SPAZIAMMINISTRATIVI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haServiziIgieniciDisabili, Literal(row['SERVIZIIGIENICIDISABILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haScaleNorma, Literal(row['SCALENORMA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haAscensoriDisabili, Literal(row['ASCENSOREDISABILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haSuperamentoBarriereArchitettoniche, Literal(row['SUPERAMENTOBARRIEREARCH'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haTeleriscaldamento, Literal(row['TELERISCALDAMENTO'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haAulaMagna, Literal(row['AULAMAGNA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haCentralizzatoAria, Literal(row['CENTRALIZZATOARIA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haCentralizzatoGasolio, Literal(row['CENTRALIZZATOGASOLIO'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haCentralizzatoOlioCombustibili, Literal(row['CENTRALIZZATOOLIOCOMBUSTIBILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haCorpiScaldantiElettriciAutonomi, Literal(row['CORPISCALDANTIELETTRICIAUTONOMI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haImpiantoRiscaldamento, Literal(row['IMPIANTORISCALDAMENTO'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haCondizionamentoVentilazione, Literal(row['CONDIZIONAMENTOVENTILAZIONE'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haPalestraPiscina, Literal(row['PALESTRAPISCINA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haRiscaldamentoAltraNatura, Literal(row['RISCALDAMENTOALTRANATURA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_scuola), skr.haSitoWeb, Literal(row['SITOWEB'],datatype=XSD.string)])
            g.add([URIRef(uri_scuola), skr.tipoScuola, Literal(row['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA'], datatype=XSD.string)])
            g.add([URIRef(uri_point), schema.latitude, Literal(row['LATITUDINE'])])
            g.add([URIRef(uri_point), schema.longitude, Literal(row['LONGITUDINE'])])
            g.add([URIRef(uri_scuola), skr.nomeScuola, Literal(row['NOMESCUOLA'])])
            #object properties
            g.add([URIRef(uri_scuola), skr.haPlesso, URIRef(uri_plesso)])
            g.add([URIRef(uri_scuola), skr.coordinate, URIRef(uri_point)])
            g.add([URIRef(uri_point), RDF.type, schema.GeoCoordinates])
            


            #interlink comune
            dbpedia_url="http://dbpedia.org/resource/"+str(row['DESCRIZIONECOMUNE']).title().replace(" ","_")
            r=requests.get(dbpedia_url)
            if(r.status_code==200):
                g.add([URIRef(uri_scuola), skr.comune, URIRef(dbpedia_url)])
            else:
                print(row['DESCRIZIONECOMUNE']+" --- "+dbpedia_url)
                g.add([URIRef(uri_scuola), skr.comune, Literal(row['DESCRIZIONECOMUNE'],datatype=XSD.string) ])
            #interlink nomescuola
            dbpedia_url="http://dbpedia.org/resource/"+str(urify_scuola(row['NOMESCUOLA'])).title().replace(" ","_")
            r=requests.get(dbpedia_url)
            if(r.status_code==200):
                g.add([URIRef(uri_scuola), skr.dedicataA, URIRef(dbpedia_url)])
            else:
                print(urify_scuola(row['NOMESCUOLA'])+" --- "+dbpedia_url)
                g.add([URIRef(uri_scuola), skr.dedicataA, Literal(None) ])
            

            punto_scuola=(row['LATITUDINE'],row['LONGITUDINE'])
            with open('Output_autobus.csv') as csvfile:
                punto_scuola=(row['LATITUDINE'],row['LONGITUDINE'])
                reader_autobus = csv.DictReader(csvfile)
                for row in reader_autobus:
                    uri_point = base_uri+"point/"+urify_fermata((row['NOMEFERMATA']))
                    latitudine_fermata = row['LATITUDINEFERMATA']
                    longitudine_fermata = row['LONGITUDINEFERMATA']
                    nome_fermata = row['NOMEFERMATA']
                    punto_fermata = (row['LATITUDINEFERMATA'], row['LONGITUDINEFERMATA'])
                    dist = geodesic(punto_scuola, punto_fermata).meters
                    if dist < 300:
                        g.add([URIRef(uri_scuola), skr.vicinoA, URIRef(uri_point)])
            

            
#Da qui in poi e' per il plesso
        else:
        #Plesso
            g.add([URIRef(uri_plesso), RDF.type, skr.Plesso])
            #data properties 
            g.add([URIRef(uri_plesso), skr.valutazione, Literal(row['RANK'],datatype=XSD.float)])
            g.add([URIRef(uri_plesso), skr.haCodiceScuola, Literal(row['CODICESCUOLA'],datatype=XSD.string)])
            g.add([URIRef(uri_plesso), skr.haDescrizioneTipologiaGradoIstruzioneScuola, Literal(row['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haAccessoRampe, Literal(row['ACCESSORAMPE'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haAltriAccorgimentiDisabili, Literal(row['ALTRIACCORGIMENTIDISABILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haSpaziDidattici, Literal(row['SPAZIDIDATTICI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haSpaziAmministrativi, Literal(row['SPAZIAMMINISTRATIVI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haServiziIgieniciDisabili, Literal(row['SERVIZIIGIENICIDISABILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haScaleNorma, Literal(row['SCALENORMA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haAscensoriDisabili, Literal(row['ASCENSOREDISABILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haSuperamentoBarriereArchitettoniche, Literal(row['SUPERAMENTOBARRIEREARCH'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haTeleriscaldamento, Literal(row['TELERISCALDAMENTO'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haAulaMagna, Literal(row['AULAMAGNA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haCentralizzatoAria, Literal(row['CENTRALIZZATOARIA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haCentralizzatoGasolio, Literal(row['CENTRALIZZATOGASOLIO'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haCentralizzatoOlioCombustibili, Literal(row['CENTRALIZZATOOLIOCOMBUSTIBILI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haCorpiScaldantiElettriciAutonomi, Literal(row['CORPISCALDANTIELETTRICIAUTONOMI'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haImpiantoRiscaldamento, Literal(row['IMPIANTORISCALDAMENTO'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haCondizionamentoVentilazione, Literal(row['CONDIZIONAMENTOVENTILAZIONE'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haPalestraPiscina, Literal(row['PALESTRAPISCINA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haRiscaldamentoAltraNatura, Literal(row['RISCALDAMENTOALTRANATURA'],datatype=XSD.boolean)])
            g.add([URIRef(uri_plesso), skr.haSitoWeb, Literal(row['SITOWEB'],datatype=XSD.string)])
            g.add([URIRef(uri_plesso), skr.tipoScuola, Literal(row['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA'], datatype=XSD.string)])
            g.add([URIRef(uri_point), schema.latitude, Literal(row['LATITUDINE'])])
            g.add([URIRef(uri_point), schema.longitude, Literal(row['LONGITUDINE'])])
            g.add([URIRef(uri_plesso), skr.nomeScuola, Literal(row['NOMESCUOLA'])])

            #object properties
            g.add([URIRef(uri_plesso), skr.coordinate, URIRef(uri_point)])
            g.add([URIRef(uri_point), RDF.type, schema.GeoCoordinates])

            
            #interlink comune
            dbpedia_url="http://dbpedia.org/resource/"+str(row['DESCRIZIONECOMUNE']).title().replace(" ","_")
            r=requests.get(dbpedia_url)
            if(r.status_code==200):
                g.add([URIRef(uri_plesso), skr.comune, URIRef(dbpedia_url)])
            else:
                print(row['DESCRIZIONECOMUNE']+" --- "+dbpedia_url)
                g.add([URIRef(uri_plesso), skr.comune, Literal(row['DESCRIZIONECOMUNE'],datatype=XSD.string)])
            #interlink nomescuola
            dbpedia_url="http://dbpedia.org/resource/"+str(urify_scuola(row['NOMESCUOLA'])).title().replace(" ","_")
            r=requests.get(dbpedia_url)
            if(r.status_code==200):
                g.add([URIRef(uri_plesso), skr.dedicataA, URIRef(dbpedia_url)])
            else:
                print(urify_scuola(row['NOMESCUOLA'])+" --- "+dbpedia_url)
                g.add([URIRef(uri_plesso), skr.dedicataA, Literal(None)])
            

            punto_scuola=(row['LATITUDINE'],row['LONGITUDINE'])
            with open('Output_autobus.csv') as csvfile:
                reader_autobus = csv.DictReader(csvfile)
                for row in reader_autobus:
                    uri_point = base_uri+"point/"+urify_fermata((row['NOMEFERMATA']))
                    latitudine_fermata = row['LATITUDINEFERMATA']
                    longitudine_fermata = row['LONGITUDINEFERMATA']
                    nome_fermata = row['NOMEFERMATA']
                    punto_fermata = (row['LATITUDINEFERMATA'], row['LONGITUDINEFERMATA'])
                    dist = geodesic(punto_scuola, punto_fermata).meters
                    if dist < 300:
                        g.add([URIRef(uri_plesso), skr.vicinoA, URIRef(uri_point)])
            
g.serialize(destination='Dataset_finale.ttl', format='turtle')



