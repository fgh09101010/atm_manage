from django.urls import path
from . import views


#app_name = 'atm'

urlpatterns = [
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('chart/', views.chart, name='chart'),
    path('atmlist/', views.AtmListView.as_view(), name='atms'),
    path("atmdetail/<pk>/", views.AtmDetailView.as_view(), name="atm_detail"),
    path("address/<pk>/", views.AddressDetailView.as_view(), name="address_detail"),
    path("city/<pk>/", views.CityDetailView.as_view(), name="city_detail"),

]
