from django.shortcuts import render
from .models import AtmAddress,AtmMain,City
import random
from django.db.models import Count
import folium
from folium.plugins import MarkerCluster
from django.core.cache import cache
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
import os


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
    }


    return render(request, 'chart.html', chart_data)

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
        current_address = self.get_object().address
        atm_count = AtmMain.objects.filter(address=current_address).count()
        context['atm_count'] = atm_count
        return context


class CityDetailView(generic.DetailView):
    model = AtmMain
    template_name = 'city_detail.html'
    context_object_name = 'atm'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_address = self.get_object().city_town
        atm_count = AtmMain.objects.filter(city_town=current_address).count()
        context['atm_count'] = atm_count
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
    



    context = {'map': "成功"}

    return render(request, 'restart_map.html', context)