from django.urls import path, include
from . import views
from django.urls import path
from django.views.generic import TemplateView

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
    path('chart/use_atm', views.use_atm_chart, name='chart_use_atm'),
    path('chart/chart_atm_bank', views.atm_bank_chart, name='chart_atm_bank'),

    path("restart_map/", views.restart_map, name="restart"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('customer_list/', views.customer_list, name='customer_list'),
    path('customer/<int:customer_id>', views.customer_detail, name='customer_detail'),

    path('my_detail/', views.my_detail, name='my_detail'),

    path('atm_map_search/', views.atm_map_search, name='atm_map_search'),

    path('captcha/', include('captcha.urls')),

    path('rate/', TemplateView.as_view(template_name='rate.html'), name='rate'),
    path('exchange-rate/', views.exchange_rate, name='exchange_rate'),
    path('convert/', views.convert_currency, name='convert_currency'),
    path('result/', views.result, name = 'result'),


    path('users/', views.user_list, name='user_list'),
    path('users/<str:user_id>/', views.user_detail, name='user_detail'),

    path('atm_filter/', views.atm_filter, name='atm_filter'),

    path('atmdetail/<pk>/use', views.atm_detail_use, name = "atm_detail_use"),
    path('atmdetail/<pk>/use/deposit/', views.use_deposit, name='use_deposit'),
    path('atmdetail/<pk>/use/withdraw/', views.use_withdraw, name='use_withdraw'),
    path('atmdetail/<pk>/use/transfer/', views.use_transfer, name='use_transfer'),


]
