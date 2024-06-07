from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import auth
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from django.urls import reverse


class AtmAddress(models.Model):
    address_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True)
    english_address = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'atm_address'
        verbose_name_plural = "ATM Addresses"

    def __str__(self):
        return self.address


class City(models.Model):
    city_town_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=3, db_collation='utf8mb4_general_ci', blank=True, null=True)
    town = models.CharField(max_length=4, db_collation='utf8mb4_general_ci', blank=True, null=True)
    population = models.IntegerField()
    area = models.FloatField()
    density = models.IntegerField()

    class Meta:
        #managed = False
        db_table = 'atm_city'
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.city}{self.town}"

    def get_absolute_url(self):
        return reverse('city_detail', args=[self.city_town_id])


class AtmMain(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.ForeignKey(AtmAddress, models.DO_NOTHING, blank=True, null=True)
    city_town = models.ForeignKey(City, models.DO_NOTHING, blank=True, null=True)
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
        #managed = False
        db_table = 'atm_main'
        verbose_name_plural = "ATM Main"

    def __str__(self):
        return f"{self.atm_name}({self.id})"


class Customer(models.Model):
    user = models.OneToOneField(auth.models.User, on_delete=models.CASCADE, null=True)
    account_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    join_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Customer'
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.user} {self.account_number}"

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    atm = models.ForeignKey(AtmMain, on_delete=models.CASCADE, related_name='atm', blank=True, null=True)
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
    ]

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default="")
    destination_account = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='destination_account', null=True, blank=True)

    class Meta:
        db_table = 'Transaction'
        verbose_name_plural = "Transactions"

@receiver(pre_save, sender=Customer)
def generate_account_number(sender, instance, **kwargs):
    if not instance.account_number:
        unique_id = uuid.uuid4().hex[:6]
        next_account_number = f'000-{unique_id}'
        instance.account_number = next_account_number
