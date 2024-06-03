from django.contrib import admin
from .models import AtmAddress,AtmMain,City,Customer,Transaction

@admin.register(AtmAddress)
class AtmAddressAdmin(admin.ModelAdmin):
    list_display = ("address_id","address","english_address","longitude","latitude")

@admin.register(AtmMain)
class AtmMainAdmin(admin.ModelAdmin):
    list_display = ("address", "city_town", "atm_code", "atm_name", "type", "category", "atm_install", "phone", "service_type", "use_wheel", "voice")

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display =("city_town_id", "city", "town", "population", "area", "density")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display =("name", "account_number", "password", "balance")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display =("Customer", "time", "amount")