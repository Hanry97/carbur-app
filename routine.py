#https://www.prix-carburants.gouv.fr/rubrique/opendata/

import wget
import os
from zipfile import ZipFile
import xmltodict
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import schedule
import time
import progressbar

APP_NAME = 'carbur-app'
BACKOFF_TIME = 2
coordinatesUpdated = 0
MAX_GEOLOC_TRY = 10

def getFileFromOfficialWebSite():
    #get and extract zip file
    url = 'https://donnees.roulez-eco.fr/opendata/instantane'
    filename = wget.download(url)
    with ZipFile(filename, 'r') as zipObj:
        zipObj.extractall()

    #convert into json
    with open('PrixCarburants_instantane.xml', 'r') as xml_file:
        parsedFile = xmltodict.parse(xml_file.read(), attr_prefix='')
        xml_file.close()

        json_data = json.dumps(parsedFile)
        with open("PointsDeVente.json", "w") as json_file: 
            json_file.write(json_data) 
            json_file.close()

    #remove zip
    try:
        os.remove(filename)
    except OSError:
        pass

def getJsonData(path):
        
    jsonFile = open(path)
    data = json.load(jsonFile)
    jsonFile.close()

    return data["pdv_liste"]["pdv"]

def updateCoordinates(adress):
    geolocator = Nominatim(user_agent=APP_NAME)   
    location = None
    isLocationGet = False
    numberOfConnectionTry = 1

    while isLocationGet == False and numberOfConnectionTry <= MAX_GEOLOC_TRY:
        try:
            location = geolocator.geocode(adress, timeout=None)
            isLocationGet = True
        except :
            program_slepp()   
            numberOfConnectionTry += 1             
    
    if numberOfConnectionTry == MAX_GEOLOC_TRY and isLocationGet == False:
        print("[Program Stoped...] max number of geoloc connection try reached")
        quit()

    coord = {}
    if location is not None:   
        coord['lat']=location.latitude
        coord['lng']=location.longitude
        
    return coord
 
def program_slepp():
    print("[start sleep...] ", coordinatesUpdated, " coordinates updated")
    time.sleep(BACKOFF_TIME * 60)
    print("[Program resumes...]")

def correctGpsCoordinates():
    geolocator = Nominatim(user_agent=APP_NAME)
    data = getJsonData("PointsDeVente.json")
    global coordinatesUpdated

    with progressbar.ProgressBar(max_value=len(data)) as bar:
        count = 1
        for pdv in data :
            if -90 <= float(pdv['latitude']) <= 90 and -180 <= float(pdv['longitude']) <= 180:
                pdv_coordinate = pdv['latitude']+", "+pdv['longitude']
                location = None
                isLocationGet = False
                numberOfConnectionTry = 1

                while isLocationGet == False and numberOfConnectionTry <= MAX_GEOLOC_TRY:
                    try:
                        location = geolocator.reverse(pdv_coordinate, timeout=None)
                        isLocationGet = True
                    except:
                        program_slepp()
                        numberOfConnectionTry += 1

                if numberOfConnectionTry == MAX_GEOLOC_TRY and isLocationGet == False:
                    print("[Program Stoped...] max number of geoloc connection try reached")
                    quit()
                
                if location is not None:
                    city = location.address.split(",")
                    if pdv['ville'].upper() != city[2].lstrip().rstrip().upper():
                        real_coord = updateCoordinates(adress = pdv['adresse']+" "+pdv['ville'])
                        if bool(real_coord):
                            pdv['latitude'] = real_coord['lat']
                            pdv['longitude'] = real_coord['lng']
                        else:
                            pdv['latitude'] = 0
                            pdv['longitude'] = 0
                coordinatesUpdated += 1

            else:
                adress = pdv['adresse']+" "+pdv['ville']
                real_coord = updateCoordinates(adress)
                if bool(real_coord):
                    pdv['latitude'] = real_coord['lat']
                    pdv['longitude'] = real_coord['lng']
                else:
                    pdv['latitude'] = 0
                    pdv['longitude'] = 0
                coordinatesUpdated += 1
            
            bar.update(count)
            count += 1

    pointsDeventeValides = [pdv for pdv in data if pdv['latitude'] != 0]
    json_data = json.dumps(pointsDeventeValides)
    
    with open("PointsDeVenteTraited.json", "w") as json_file: 
        json_file.write(json_data) 
        json_file.close()

def setCoordonneesToStandardFormat():
    data = getJsonData("PointsDeVente.json")
    for pdv in data :
        pdv['latitude'] = float(pdv['latitude']) / 100000
        pdv['longitude'] = float(pdv['longitude']) / 100000

    json_data = json.dumps(data)
    
    with open("PointsDeVenteTraited.json", "w") as json_file: 
        json_file.write(json_data) 
        json_file.close()
    
    isExist = os.path.exists("carbur_backend/PointsDeVenteTraited.json")
    if isExist :
        os.remove("carbur_backend/PointsDeVenteTraited.json")

    os.replace("PointsDeVenteTraited.json", "carbur_backend/PointsDeVenteTraited.json")
    os.remove("PointsDeVente.json")
    os.remove("PrixCarburants_instantane.xml")

def job():
    getFileFromOfficialWebSite()
    print ("\n[OK]-getFileFromOfficialWebSite")

    setCoordonneesToStandardFormat()
    print ("[OK]-setCoordinatesToStandardVersion")

# schedule.every().day.at("09:00").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
job()



