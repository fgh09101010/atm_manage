from django.shortcuts import render, redirect, get_object_or_404
from .models import AtmAddress,AtmMain,City,Customer,Transaction
import random
from django.db.models import Count, functions
import folium
from folium.plugins import MarkerCluster
from django.core.cache import cache
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
import os
from .forms import RegisterForm,LoginForm,DepositForm,WithdrawForm,TransferForm,PaymentForm,FilterForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.db import models
import datetime
from django.utils import timezone
from django.utils.timezone import activate
from django.db.models import Sum
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template.loader import get_template, TemplateDoesNotExist
from .forms import ContactForm
# Create your views here.

def time_to_minute(x):
    x=x.split(":")
    return int(x[0])*60+int(x[1])


def index(request):
    atm_address=AtmAddress.objects.all()
    context={
        "atm_address":atm_address
    }
    return render(request, 'index.html',context=context)

def map(request):
    template_name = "all_atm_map.html"
    template_exists = False
    try:
        get_template(template_name)
        template_exists = True
    except TemplateDoesNotExist:
        template_exists = False

    return render(request, 'map.html', {'template_exists': template_exists})

def chart(request):
    city_atm_counts = AtmMain.objects.values('city_town__city').annotate(total=Count('city_town')).order_by('-total', 'city_town__city')

    # 分離標籤和數據
    labels = [item['city_town__city'] for item in city_atm_counts]
    values = [item['total'] for item in city_atm_counts]

    colors = [f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}' for _ in city_atm_counts]
    background_colors = [ _+", 0.2)" for _ in colors]
    border_colors = [ _+", 1.0)" for _ in colors]

    # 將圖表數據儲存到緩存中，有效期可以自行設置
    chart_data = {
        'labels': labels,
        'values': values,
        'background_colors': background_colors,
        'border_colors': border_colors,
        "atm_count":AtmMain.objects.count(),
    }


    return render(request, 'chart_atm.html', chart_data)

class AtmListView(generic.ListView):
    model = AtmMain
    context_object_name = 'atm_list'
    paginate_by = 10
    template_name = 'atm_list.html'
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return AtmMain.objects.filter(
                Q(atm_name__icontains=query) |
                Q(city_town__city__icontains=query) |
                Q(city_town__town__icontains=query) |
                Q(address__address__icontains=query)
            ).order_by('id')
        else:
            return AtmMain.objects.all().order_by('id')


class AtmDetailView(generic.DetailView):
    model = AtmMain
    template_name = 'atm_detail.html'
    context_object_name = 'atm'

    def get_queryset(self):
        return super().get_queryset().select_related('address', 'city_town')
    



class AddressDetailView(generic.DetailView):
    model = AtmAddress
    template_name = 'address_detail.html'
    context_object_name = 'address'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = self.get_object()
        atm_main_instance = AtmMain.objects.filter(address=address).first()
        context['atm_count'] = AtmMain.objects.filter(address=address).count()
        context['city_town'] = atm_main_instance.city_town if atm_main_instance else "Unknown"
        context['id'] = address.address_id  # 使用 address_id 而不是 id
        return context

class CityDetailView(generic.DetailView):
    model = City  # 將 model 設置為 City
    template_name = 'city_detail.html'
    context_object_name = 'city'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = self.get_object()  # 獲取城市對象
        atm_count = AtmMain.objects.filter(city_town=city).count()
        context["city"]=city
        context['atm_count'] = atm_count
        context['addresses'] = AtmAddress.objects.filter(atmmain__city_town=city)

        return context
    

def restart_map(request):


    m = folium.Map(location=[25.0330, 121.5654], zoom_start=12)  # Taipei 的中心經緯度
    marker_cluster = MarkerCluster(name="marker").add_to(m)

    # 從資料庫中提取所有 ATM 地址數據
    atm_main = AtmMain.objects.all()

    # 將每個 ATM 的地址經緯度添加到地圖上
    for atm in atm_main:
        latitude = atm.address.latitude
        longitude = atm.address.longitude
        ltip = atm.atm_name
        lpop=f'<a href="/atm/atmdetail/{atm.id}/" target = "_blank">More Details</a>'
        #lpop = f'<a href="http://127.0.0.1:8000/atm/atmdetail/{atm.id}/">http://127.0.0.1:8000/atm/atmdetail/</a>'
        #lpop = "<a href='http://127.0.0.1:8000/atm/atmdetail/1'>123</a>"
        if latitude and longitude:  # 確保經緯度不為空
            folium.Marker(
                [latitude, longitude],tooltip=ltip,popup=lpop
            ).add_to(marker_cluster)
        print(atm.id,latitude,longitude)
    # 將地圖渲染為 HTML 字符串
    file_path = os.path.join( "atm","templates","all_atm_map.html")  # 修改为你的 Django 项目文件夹路径
    map_html = m._repr_html_()
    #m.save(file_path)
    with open(file_path,"w",encoding="UTF-8") as data:
        data.write(map_html)
    



    context = {'map': "地圖重整成功"}

    return render(request, 'restart_map.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # 创建并关联 Customer 实例
            Customer.objects.create(user=user)

            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user  != "":
                login(request, user)
                return redirect('index') 
            else:
                form.add_error(None, '用户名或密码不正确')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            customer = request.user.customer
            customer.balance += amount
            customer.save()

            # 创建存款交易记录
            Transaction.objects.create(customer=customer, amount=amount, type='deposit')

            return redirect('index')  # 存款成功后重定向到主页
    else:
        form = DepositForm()
    return render(request, 'deposit.html', {'form': form})


@login_required
def withdraw(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            customer = request.user.customer

            # 检查用户余额是否足够
            if amount <= customer.balance:
                customer.balance -= amount
                customer.save()

                # 创建取款交易记录
                Transaction.objects.create(customer=customer, amount=amount, type='withdraw')

                return redirect('index')  # 取款成功后重定向到主页
            else:
                form.add_error('amount', '余额不足')
    else:
        form = WithdrawForm()
    return render(request, 'withdraw.html', {'form': form})

@login_required
def transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            source_account = request.user.customer
            destination_account_number = form.cleaned_data['destination_account_number']
            destination_account = Customer.objects.get(account_number=destination_account_number)
            amount = form.cleaned_data['amount']

            # 检查源账户余额是否足够
            if amount <= source_account.balance:
                # 更新源账户余额
                source_account.balance -= amount
                source_account.save()

                # 更新目标账户余额
                destination_account.balance += amount
                destination_account.save()

                # 创建转账交易记录
                Transaction.objects.create(customer=source_account, amount=amount, type='transfer')

                # 创建另一条转账交易记录，以记录目标账户的收入
                Transaction.objects.create(customer=destination_account, amount=amount, type='transfer', destination_account=source_account)

                return redirect('index')  # 转账成功后重定向到主页
            else:
                form.add_error('amount', '余额不足')
    else:
        form = TransferForm()
    return render(request, 'transfer.html', {'form': form})

@login_required
def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            customer = request.user.customer
            amount = form.cleaned_data['amount']


            if amount <= customer.balance:

                customer.balance -= amount
                customer.save()


                Transaction.objects.create(customer=customer, amount=amount, type='payment')

                return redirect('index')  
            else:
                form.add_error('amount', '余额不足')
    else:
        form = PaymentForm()
    return render(request, 'payment.html', {'form': form})

def registration_trend(request):
    #activate('Asia/Taipei')

    today = timezone.localtime(timezone.now()).date()


    past_month = [today - datetime.timedelta(days=i) for i in range(29, -1, -1)]


    registration_data = {
        'labels': [],
        'data': [],
        'user_count':0
    }

    for day in past_month:

        start_of_day = timezone.make_aware(datetime.datetime.combine(day, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(day, datetime.time.max))

        customers_on_day = Customer.objects.filter(join_time__range=(start_of_day, end_of_day))
        num_customers = customers_on_day.count()


        registration_data['labels'].append(day.strftime('%Y-%m-%d'))
        registration_data['data'].append(num_customers)
        registration_data['user_count']+=num_customers
    return render(request, 'chart_user.html', {'registration_data': registration_data})


def transaction_chart(request):

    today = timezone.localtime(timezone.now()).date()


    past_month = [today - datetime.timedelta(days=i) for i in range(29, -1, -1)]


    data = {
        'labels': [],
        'deposit': [],
        'withdraw': [],
        'transfer': [],
        'payment': [],
        'total':0,
    }

    for day in past_month:

        start_of_day = timezone.make_aware(datetime.datetime.combine(day, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(day, datetime.time.max))

        customers_on_day = Transaction.objects.filter(time__range=(start_of_day, end_of_day))
        num = customers_on_day


        deposit_amount = num.filter(type="deposit").aggregate(total_amount=Sum('amount'))['total_amount']
        if deposit_amount is None:deposit_amount = 0
        
        withdraw_amount = num.filter(type="withdraw").aggregate(total_amount=Sum('amount'))['total_amount']
        if withdraw_amount is None:withdraw_amount = 0

        transfer_amount = num.filter(type="transfer").aggregate(total_amount=Sum('amount'))['total_amount']
        if transfer_amount is None:transfer_amount = 0

        payment_amount = num.filter(type="payment").aggregate(total_amount=Sum('amount'))['total_amount']
        if payment_amount is None:payment_amount = 0

        data['labels'].append(day.strftime('%Y-%m-%d'))
        data['deposit'].append(float(deposit_amount))
        data['withdraw'].append(float(withdraw_amount))
        data['transfer'].append(float(transfer_amount))
        data['payment'].append(float(payment_amount))
        data['total']+=float(deposit_amount)+float(withdraw_amount)+float(transfer_amount)+float(payment_amount)
        
    return render(request, 'chart_transaction.html', {'data': data})

def my_detail(request):
    # 根據用戶名獲取相應的用戶對象
    username=request.user
    user = User.objects.get(username=username)

    # 通過用戶對象獲取相應的客戶對象
    customer = Customer.objects.get(user=user)

    # 獲取客戶的餘額
    balance = customer.balance

    # 獲取客戶的所有交易記錄
    transactions = Transaction.objects.filter(customer=customer).order_by('-time')

    # 將用戶名、餘額和交易記錄傳遞到模板中
    context = {
        'username': username,
        'balance': balance,
        'transactions': transactions,
    }

    # 渲染模板並返回 HTTP 響應
    return render(request, 'my_detail.html', context)

def atm_map_search(request):
    cities = City.objects.all()
    addresses = AtmAddress.objects.all()
    selected_city = None

    if request.method == 'GET':
        city_id = request.GET.get('city')
        if city_id:
            selected_city = City.objects.get(pk=city_id)


    return render(request, 'atm_map_search.html', {'cities': cities, 'addresses': addresses, 'selected_city': selected_city})

def map_view(request,pk):
    address = get_object_or_404(AtmAddress, pk=pk)
    context = {
        'latitude': address.latitude,
        'longitude': address.longitude,
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
    }
    return render(request, 'address_map.html', context)

def user_list(request):
    users = User.objects.all()
    context={
        "users" : users
    }
    return render(request, 'user_list.html', context=context)

def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    transactions = Transaction.objects.filter(customer__user=user).order_by('-time')
    context={   
        'user': user, 
         'transactions': transactions
    }
    return render(request, 'user_detail.html', context=context)



  
def atm_filter(request):
    form = FilterForm(request.GET or None)
    atms = None

    
    if request.GET and form.is_valid():
        city_town = form.cleaned_data.get('city_town')
        service_time = form.cleaned_data.get('service_time')
        use_wheel = form.cleaned_data.get('use_wheel')
        voice = form.cleaned_data.get('voice')
        #atm = AtmMain.objects.filter(city_town=city_town,use_wheel=use_wheel,voice=voice)
        data=AtmMain.objects.all()
        if city_town is not None:
            data = data.filter(city_town=city_town)
        
        if use_wheel  != "":
            data = data.filter(use_wheel=use_wheel)
        if voice  != "":
            
            data = data.filter(voice=voice)
        
        if service_time  != "":
            business_atms = []
            hope_time=time_to_minute(str(service_time))
            for atm in data:
                open_time,close_time=atm.service_type.split("~")
                open_time=time_to_minute(open_time)
                close_time=time_to_minute(close_time)

                if open_time <= hope_time <= close_time:
                    business_atms.append(atm)
            data = business_atms

        atm_count=len(data)
        if len(data)>=1000:
            data=data[:1000]
        atms = {
            'city_town': city_town,
            'service_time': service_time,
            'use_wheel': use_wheel,
            'voice': voice,
            'data':data,
            'atm_count':atm_count,
        }
        
    return render(request, 'atm_filter.html', {'form': form, 'atms': atms})

def atm_filter_map(request):
    data = request.GET.get('data', None)

    return render(request, 'atm_filter_map.html', {'data': data})

EXCHANGE_RATES = {
    'TW':{
        'rate': 1,
    },
    'USD': {
        'img': 'img/USD.svg',
        'spot_buy': '32.3500',
        'spot_sell': '32.4500',
        'digital_discount_buy': '32.3800',
        'digital_discount_sell': '32.4200',
        'cash_buy': '32.0700',
        'cash_sell': '32.6700',
        'rate': 32.34,
    },
    'EUR': {
        'img': 'img/EUR.svg',
        'spot_buy': '34.9400',
        'spot_sell': '35.4400',
        'digital_discount_buy': '35.0000',
        'digital_discount_sell': '35.3800',
        'cash_buy': '34.5100',
        'cash_sell': '35.7900',
        'rate': 35.21,
    },
    'JPY': {
        'img': 'img/JPY.svg',
        'spot_buy': '0.2064',
        'spot_sell': '0.2114',
        'digital_discount_buy': '0.2074',
        'digital_discount_sell': '0.2104',
        'cash_buy': '0.2024',
        'cash_sell': '0.2134',
        'rate': 0.21,
    },
    'CNY': {
        'img': 'img/CNY.svg',
        'spot_buy': '4.4300',
        'spot_sell': '4.5050',
        'digital_discount_buy': '4.4400',
        'digital_discount_sell': '4.4950',
        'cash_buy': '4.3300',
        'cash_sell': '4.5250',
        'rate': 4.46,
    },
    'HKD': {
        'img': 'img/HKD.svg',
        'spot_buy': '4.1120',
        'spot_sell': '4.1820',
        'digital_discount_buy': '4.1220',
        'digital_discount_sell': '4.1720',
        'cash_buy': '4.0320',
        'cash_sell': '4.2220',
        'rate': 4.14,
    },
    'AUD': {
        'img': 'img/AUD.svg',
        'spot_buy': '21.3800',
        'spot_sell': '21.6400',
        'digital_discount_buy': '21.4100',
        'digital_discount_sell': '21.6100',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 21.51,
    },
    'NZD': {
        'img': 'img/NZD.svg',
        'spot_buy': '19.8200',
        'spot_sell': '20.1200',
        'digital_discount_buy': '19.8400',
        'digital_discount_sell': '20.1000',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 20.02,
    },
    'ZAR': {
        'img': 'img/ZAR.svg',
        'spot_buy': '1.6760',
        'spot_sell': '1.7960',
        'digital_discount_buy': '1.6810',
        'digital_discount_sell': '1.7910',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 1.71,
    },
    'CAD': {
        'img': 'img/CAD.svg',
        'spot_buy': '23.4800',
        'spot_sell': '23.8800',
        'digital_discount_buy': '23.5100',
        'digital_discount_sell': '23.8500',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 23.65,
    },
    'GBP': {
        'img': 'img/GBP.svg',
        'spot_buy': '41.1100',
        'spot_sell': '41.7300',
        'digital_discount_buy': '41.1700',
        'digital_discount_sell': '41.6700',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 41.36,
    },
    'CHF': {
        'img': 'img/CHF.svg',
        'spot_buy': '36.1200',
        'spot_sell': '36.6400',
        'digital_discount_buy': '36.1500',
        'digital_discount_sell': '36.6100',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 30,
    },
    'SEK': {
        'img': 'img/SEK.svg',
        'spot_buy': '3.0400',
        'spot_sell': '3.1600',
        'digital_discount_buy': '3.0500',
        'digital_discount_sell': '3.1500',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 30,
    },
    'SGD': {
        'img': 'img/SGD.svg',
        'spot_buy': '23.8500',
        'spot_sell': '24.1500',
        'digital_discount_buy': '23.8800',
        'digital_discount_sell': '24.1200',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 30,
    },
    'THB': {
        'img': 'img/THB.svg',
        'spot_buy': '0.8510',
        'spot_sell': '0.9110',
        'digital_discount_buy': '0.8540',
        'digital_discount_sell': '0.9080',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 30,
    },
    'DKK': {
        'img': 'img/DKK.svg',
        'spot_buy': '4.6300',
        'spot_sell': '4.7900',
        'digital_discount_buy': '4.6400',
        'digital_discount_sell': '4.7800',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 30,
    },
    'TRY': {
        'img': 'img/TRY.svg',
        'spot_buy': '0.6340',
        'spot_sell': '1.3540',
        'digital_discount_buy': '0.6640',
        'digital_discount_sell': '1.3240',
        'cash_buy': '--',
        'cash_sell': '--',
        'rate': 30,
    },
}

def exchange_rate(request):
    currency = request.GET.get('currency', 'USD')
    rates = EXCHANGE_RATES.get(currency, None)
    context = {
        'currency': currency,
        'rates': rates,
    }
    return render(request, 'exchange_rate.html', context)


def convert_currency(request):
    return render(request, 'convert.html')

def result(request):
    
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        from_currency = request.POST['from_currency']
        to_currency = request.POST['to_currency']

        from_rate = EXCHANGE_RATES.get(from_currency, {}).get('rate', None)
        to_rate = EXCHANGE_RATES.get(to_currency, {}).get('rate', None)

        if from_rate is None or to_rate is None:
            converted_amount = None
        else:
            converted_amount = round(amount / (to_rate / from_rate), 2)

        context = {
            'amount': amount,
            'from_currency': from_currency,
            'to_currency': to_currency,
            'converted_amount': converted_amount,
            'from_img': EXCHANGE_RATES.get(from_currency, {}).get('img', ''),
            'to_img': EXCHANGE_RATES.get(to_currency, {}).get('img', '')
        }
        return render(request, 'result.html', context)
    

def rate(request):
    return render(request, 'rate.html')

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    return render(request, 'customer_detail.html', {'customer': customer})

def atm_copy(request):
    return render(request, 'index_copy.html')




