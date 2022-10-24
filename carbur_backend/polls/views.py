from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from polls.manageJsonFiles import GpsDataCollection



def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def maps_view(request):       
    data = GpsDataCollection("PointsDeVenteTraited.json")
    cities = data.getListOfCities()
    context = {
      'cities': cities,
      'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    
    return render(request, 'map.html', context)

@csrf_exempt
def getPointsDeVenteByLocation(request):
    
    if request.method == 'POST':
        position = json.loads(request.body)
        lat = position.get('lat')
        lng = position.get('lng')
        
        data = GpsDataCollection("PointsDeVenteTraited.json")
        
        center = (lat, lng)
        radius = 25
        return JsonResponse(data.searchByCircle(center,radius), safe=False)

@csrf_exempt
def getPointsDeVenteByCityAndCarburant(request):
    data = GpsDataCollection("PointsDeVenteTraited.json")
    filtre = json.loads(request.body)
    city = filtre.get('city')
    carburant = filtre.get('carburants')

    return JsonResponse(data.getPointsDeVenteByCityAndCarburant(city,carburant), safe=False)

@csrf_exempt
def getCityCoords(request):
    data = GpsDataCollection("PointsDeVenteTraited.json")
    cityname = json.loads(request.body).get('city')

    return JsonResponse(data.getCityCoords(cityname), safe=False)

@csrf_exempt
def getPointsDeVenteByRadiusAndCarburant(request):
    data = GpsDataCollection("PointsDeVenteTraited.json")
    filtre = json.loads(request.body)
    radius = filtre.get('radius')
    center = (filtre.get('lat'), filtre.get('lng'))
    carburant = filtre.get('carburants')

    return JsonResponse(data.getPointsDeVenteByRadiusAndCarburant(center, radius, carburant), safe=False)