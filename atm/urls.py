from django.urls import path
from . import views
from django.urls import path
from django.views.generic import TemplateView

#app_name = 'atm'

urlpatterns = [
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('atmlist/', views.AtmListView.as_view(), name='atms'),
    path("atmdetail/<pk>/", views.AtmDetailView.as_view(), name="atm_detail"),
    path("address/<pk>/", views.AddressDetailView.as_view(), name="address_detail"),
    path('address/<int:pk>/map', views.map_view, name='map_view'),
    path("city/<pk>/", views.CityDetailView.as_view(), name="city_detail"),

    path('chart/atm', views.chart, name='chart_atm'),
    path('chart/user', views.registration_trend, name='chart_user'),
    path('chart/transaction', views.transaction_chart, name='chart_transaction'),


    path("restart_map/", views.restart_map, name="restart"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer, name='transfer'),
    path('payment/', views.payment, name='payment'),

    path('customer_detail', views.customer_detail, name='customer_detail'),

    path('atm_map_search/', views.atm_map_search, name='atm_map_search'),

    

    path('rate/', TemplateView.as_view(template_name='rate.html'), name='rate'),
    path('exchange-rate/', TemplateView.as_view(template_name='exchange_rate.html'), name='exchange_rate'),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),

    path('atm_filter/', views.atm_filter, name='atm_filter'),


]
