from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class AtmAddress(models.Model):
    address_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True)
    english_address = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atm_address'
        verbose_name_plural = "atm_address"

    def __str__(self):
        return self.address


class AtmMain(models.Model):
    address = models.ForeignKey(AtmAddress, models.DO_NOTHING, blank=True, null=True)
    city_town = models.ForeignKey("City", models.DO_NOTHING, blank=True, null=True)
    atm_code = models.CharField(max_length=10, db_collation='utf8mb4_general_ci', blank=True, null=True)
    atm_name = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True)
    type = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True)
    category = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True)
    atm_install = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True)
    phone = models.CharField(max_length=200, db_collation='utf8mb4_general_ci', blank=True, null=True)
    service_type = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True)
    use_wheel = models.CharField(max_length=100, db_collation='utf8mb4_general_ci', blank=True, null=True)
    voice = models.CharField(max_length=100, db_collation='utf8mb4_general_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atm_main'
        verbose_name_plural = "atm_main"
    
    def __str__(self):
        return self.atm_name


class City(models.Model):
    city_town_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=3, db_collation='utf8mb4_general_ci', blank=True, null=True)
    town = models.CharField(max_length=4, db_collation='utf8mb4_general_ci', blank=True, null=True)
    population = models.IntegerField()
    area = models.FloatField()
    density = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'atm_city'
        verbose_name_plural = "atm_city"

    def __str__(self):
        return f"{self.city}{self.town}"
    
class Customer(models.Model):
    name=models.CharField(max_length=1000, db_collation='utf8mb4_general_ci', blank=True, null=True)
    account_number=models.CharField(max_length=1000, db_collation='utf8mb4_general_ci', blank=True, null=True)
    password=models.CharField(max_length=1000, db_collation='utf8mb4_general_ci', blank=True, null=True)
    balance=models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        db_table = 'Customer'
        verbose_name_plural = "Customer"

    def __str__(self):
        return f"{self.name}"
    
class Transaction(models.Model):
    Customer = models.ForeignKey(Customer, models.DO_NOTHING, blank=True, null=True)
    time = models.DateTimeField(auto_now=True)
    amount=models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    #轉入銀行
    #轉入帳號
    class Meta:
        db_table = 'Transaction'
        verbose_name_plural = "Transaction"
