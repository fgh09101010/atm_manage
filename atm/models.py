from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import auth
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from django.urls import reverse


class AtmAddress(models.Model):
    address_id = models.AutoField(primary_key=True,verbose_name="address_id")
    address = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="地址")
    english_address = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="英文地址")
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True,verbose_name="經度")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True,verbose_name="緯度")

    class Meta:
        #managed = False
        db_table = 'atm_address'
        verbose_name_plural = "地址"

    def __str__(self):
        return self.address


class City(models.Model):
    city_town_id = models.AutoField(primary_key=True,verbose_name="city_town_id")
    city = models.CharField(max_length=3, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="縣市")
    town = models.CharField(max_length=4, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="鄉鎮")
    population = models.IntegerField(verbose_name="人口")
    area = models.FloatField(verbose_name="面積")
    density = models.IntegerField(verbose_name="密度")

    class Meta:
        #managed = False
        db_table = 'atm_city'
        verbose_name_plural = "城市"

    def __str__(self):
        return f"{self.city}{self.town}"

    def get_absolute_url(self):
        return reverse('city_detail', args=[self.city_town_id])


class AtmMain(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="ID")
    address = models.ForeignKey(AtmAddress, models.DO_NOTHING, blank=True, null=True,verbose_name="地址")
    city_town = models.ForeignKey(City, models.DO_NOTHING, blank=True, null=True,verbose_name="地區")
    atm_code = models.CharField(max_length=10, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="ATM銀行代碼")
    atm_name = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="ATM銀行名稱")
    type = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="類型")
    category = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="類別")
    atm_install = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="安裝地點")
    phone = models.CharField(max_length=200, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="電話")
    service_type = models.CharField(max_length=500, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="營業時間")
    use_wheel = models.CharField(max_length=100, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="支援輪椅使用")
    voice = models.CharField(max_length=100, db_collation='utf8mb4_general_ci', blank=True, null=True,verbose_name="支援聽障使用")

    class Meta:
        #managed = False
        db_table = 'atm_main'
        verbose_name_plural = "ATM"

    def __str__(self):
        return f"{self.atm_name}({self.id})"


class Customer(models.Model):
    user = models.OneToOneField(auth.models.User, on_delete=models.CASCADE, null=True,verbose_name="使用者帳號")
    account_number = models.CharField(max_length=100, unique=True, blank=True, null=True,verbose_name="銀行帳號")
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0,verbose_name="餘額")
    join_time = models.DateTimeField(auto_now_add=True,verbose_name="加入時間")

    class Meta:
        db_table = 'Customer'
        verbose_name_plural = "顧客"

    def __str__(self):
        return f"{self.user} {self.account_number}"

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE,verbose_name="使用者")
    time = models.DateTimeField(auto_now_add=True,verbose_name="交易時間")
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,verbose_name="金額")
    atm = models.ForeignKey(AtmMain, on_delete=models.CASCADE, related_name='atm', blank=True, null=True,verbose_name="使用atm")
    TRANSACTION_TYPES = [
        ('deposit', '存款'),
        ('withdraw', '取款'),
        ('transfer', '轉帳'),
        ('payment', '付款'),
    ]

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default="",verbose_name="交易類型")
    destination_account = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='destination_account', null=True, blank=True,verbose_name="來自銀行帳號")

    class Meta:
        db_table = 'Transaction'
        verbose_name_plural = "交易"

    def get_atm_name(self):
        return f"{self.atm}"


@receiver(pre_save, sender=Customer)
def generate_account_number(sender, instance, **kwargs):
    if not instance.account_number:
        unique_id = uuid.uuid4().hex[:6]
        next_account_number = f'000-{unique_id}'
        instance.account_number = next_account_number
