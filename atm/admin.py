from django.contrib import admin
from .models import AtmAddress,AtmMain,City,Customer,Transaction

@admin.register(AtmAddress)
class AtmAddressAdmin(admin.ModelAdmin):
    list_display = ("address_id","address","english_address","longitude","latitude")
    search_fields = ("address", "english_address")

@admin.register(AtmMain)
class AtmMainAdmin(admin.ModelAdmin):
    list_display = ("address", "city_town", "atm_code", "atm_name", "type", "category", "atm_install", "phone", "service_type", "use_wheel", "voice")
    list_filter = ("city_town__city","type", "use_wheel", "voice",)
    search_fields = ("address", "city_town" , "atm_code", "atm_name", "phone",)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display =("city_town_id", "city", "town", "population", "area", "density")
    list_filter = ("city",)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display =("user", "balance","account_number","join_time")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'time', 'amount', 'type',  'destination_account','atm']
    list_filter = ("type",)