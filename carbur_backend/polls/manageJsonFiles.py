import json
from collections import Counter
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from django.http import JsonResponse

APP_NAME = 'carbur-app'


class GpsDataCollection:

    def __init__(self, json_data_path):
        self.jsonObject = self.getJsonData(json_data_path)

    def getJsonData(self, path):

        jsonFile = open(path)
        data = json.load(jsonFile)
        jsonFile.close()

        return data

    def getNumberOfPointsDeVente(self):
        return len(self.jsonObject)

    def getCityNumberOfPointsDeVente(self, cityName):
        data = self.jsonObject
        numberOFpdv = Counter(k[:] for d in data for k, v in d.items() if k.startswith(
            'ville') and v.upper().startswith(cityName.upper()))
        return numberOFpdv['ville']

    def searchByCity(self, cityName):

        data = self.jsonObject
        pointsDeVente = json.dumps(
            [pointDevente for pointDevente in data if pointDevente['ville'].upper() == cityName.upper()])

        return json.loads(pointsDeVente)

    def searchByCircle(self, center, radius):

        pointsDeVente = []
        data = self.jsonObject

        for pdv in data:
            pdv_coordinate = (float(pdv['latitude']), float(pdv['longitude']))
            if geodesic(center, pdv_coordinate).km <= radius:
                pointsDeVente.append(pdv)

        return json.loads(json.dumps(pointsDeVente))

    def getCityNameFromCoords(self, lat, lng):
        geolocator = Nominatim(user_agent=APP_NAME)
        pdv_coordinate = str(lat)+", "+str(lng)
        location = geolocator.reverse(pdv_coordinate, timeout=None)
        loc_dict = location.raw
        return loc_dict['address']['city']

    def getCityCoords(self, cityname):
        geolocator = Nominatim(user_agent=APP_NAME)
        location = geolocator.geocode(cityname)
        position = {"lat":location.latitude,"lng":location.longitude}

        return position

    def getListOfCities(self):
        cities = []
        data = self.jsonObject

        for pdv in data:
            if pdv['ville'].capitalize() not in cities:
                cities.append(pdv['ville'].capitalize())

        cities.sort()
        return cities

    def getPointsDeVenteByCityAndCarburant(self, city, carburants):

        pointsDeVente = []
        data = self.jsonObject
        carburants = [x.lower() for x in carburants]
        
        for pdv in data:
            if pdv['ville'].upper() == city.upper():
                if len(carburants) > 0:
                    if "prix" in pdv:
                        if isinstance(pdv["prix"], list):
                            for i in range(len(pdv["prix"])):
                                if pdv["prix"][i]["nom"].lower() in carburants:
                                    pointsDeVente.append(pdv)
                                    break
                        else:
                            if pdv["prix"]["nom"].lower() in carburants:
                                pointsDeVente.append(pdv)
                else:
                    pointsDeVente.append(pdv)  

        return json.loads(json.dumps(pointsDeVente))

    def getPointsDeVenteByRadiusAndCarburant(self, center, radius, carburants):
    
        pointsDeVente = []
        data = self.jsonObject
        carburants = [x.lower() for x in carburants]     
        radius = float(radius)

        for pdv in data:
            pdv_coordinate = (float(pdv['latitude']), float(pdv['longitude']))
            if geodesic(center, pdv_coordinate).km <= radius:
                if len(carburants) > 0:
                    if "prix" in pdv:
                        if isinstance(pdv["prix"], list):
                            for i in range(len(pdv["prix"])):
                                if pdv["prix"][i]["nom"].lower() in carburants:
                                    pointsDeVente.append(pdv)
                                    break
                        else:
                            if pdv["prix"]["nom"].lower() in carburants:
                                pointsDeVente.append(pdv)
                else:
                    pointsDeVente.append(pdv)

        return json.loads(json.dumps(pointsDeVente))  


#data = GpsDataCollection("PointsDeVenteTraited.json")
#myPosition = (43.516650580276526, 5.455939784654437)
#print (data.searchByCircle(myPosition,5))