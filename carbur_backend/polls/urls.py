from django.urls import path
from . import views

urlpatterns = [
    path('', views.maps_view, name="maps_view"),
    path('map/', views.maps_view, name="maps_view"),
    path('pdv/', views.getPointsDeVenteByLocation, name="getPointsDeVenteByLocation"),
    path('pdv/city-carburant/', views.getPointsDeVenteByCityAndCarburant, name="getPointsDeVenteByCityAndCarburant"),
    path('pdv/city-location/', views.getCityCoords, name="getCityCoords"),
    path('pdv/city-radius/', views.getPointsDeVenteByRadiusAndCarburant, name="getPointsDeVenteByRadiusAndCarburant"),
]