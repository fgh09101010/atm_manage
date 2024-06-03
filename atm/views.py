from django.shortcuts import render
from .models import AtmAddress,AtmMain,City
import random
from django.db.models import Count
import folium
from folium.plugins import MarkerCluster
from django.core.cache import cache
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
# Create your views here.
def index(request):
    atm_address=AtmAddress.objects.all()
    context={
        "atm_address":atm_address
    }
    return render(request, 'index.html',context=context)

def map(request):
    map_html = cache.get('map_html')
    if not map_html:
        m = folium.Map(location=[25.0330, 121.5654], zoom_start=12)  # Taipei 的中心經緯度
        marker_cluster = MarkerCluster(name="marker").add_to(m)

        # 從資料庫中提取所有 ATM 地址數據
        atm_main = AtmMain.objects.all()
        atm_coordinates = AtmMain.objects.values('address__latitude', 'address__longitude')

        # 將每個 ATM 的地址經緯度添加到地圖上
        for atm in atm_main:
            latitude = atm.address.latitude
            longitude = atm.address.longitude
            ltip = atm.atm_name
            lpop=f'<a href="/atm/atmdetail/{atm.id}/">More Details</a>'
            #lpop = f'<a href="http://127.0.0.1:8000/atm/atmdetail/{atm.id}/">http://127.0.0.1:8000/atm/atmdetail/</a>'
            #lpop = "<a href='http://127.0.0.1:8000/atm/atmdetail/1'>123</a>"
            if latitude and longitude:  # 確保經緯度不為空
                folium.Marker(
                    [latitude, longitude],tooltip=ltip,popup=lpop
                ).add_to(marker_cluster)
            print(latitude)
        # 將地圖渲染為 HTML 字符串
        map_html = m._repr_html_()

        # 將地圖 HTML 字符串儲存到緩存中，有效期可以自行設置
        cache.set('map_html', map_html, timeout=3600)  # 這裡的 timeout 可以根據需要自行設置

    # 將地圖 HTML 字符串傳遞給模板
    context = {'map': map_html}

    return render(request, 'map.html', context)

def chart(request):
    chart_data = cache.get('chart_data')
    if not chart_data:
        city_atm_counts = AtmMain.objects.values('city_town__city').annotate(total=Count('city_town')).order_by('city_town__city')

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
        cache.set('chart_data', chart_data, timeout=3600)  # 這裡的 timeout 可以根據需要自行設置

    return render(request, 'chart.html', chart_data)

class AtmListView(generic.ListView):
    model = AtmMain
    context_object_name = 'atm_list'
    paginate_by = 10
    #queryset = Book.objects.filter(title__icontains='war')[:5]
    template_name = 'atm_list.html'

class AtmDetailView(generic.DetailView):
    model = AtmMain
    template_name = 'atm_detail.html'
    context_object_name = 'atm'