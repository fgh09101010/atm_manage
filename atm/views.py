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
from .forms import RegisterForm,LoginForm,DepositForm,WithdrawForm,TransferForm,PaymentForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import models
from datetime import datetime
from django.utils import timezone
import datetime
from django.utils.timezone import activate
from django.db.models import Sum
from django.contrib.auth.models import User


# Create your views here.
def index(request):
    atm_address=AtmAddress.objects.all()
    context={
        "atm_address":atm_address
    }
    return render(request, 'index.html',context=context)

def map(request):



    return render(request, 'map.html')

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
    model = AtmMain
    template_name = 'address_detail.html'
    context_object_name = 'atm'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atm = self.get_object()
        address = atm.address
        context['atm_count'] = AtmMain.objects.filter(address=address).count()
        context['city_town'] = atm.city_town  # 使用 atm 对象的 city_town 属性
        
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
        print(latitude)
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
            if user is not None:
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

def customer_detail(request, username):
    # 根據用戶名獲取相應的用戶對象
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
    return render(request, 'customer_detail.html', context)