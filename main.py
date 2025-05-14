from flask import Flask, render_template
import folium
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Tạo geolocator để tìm kiếm vị trí
geolocator = Nominatim(user_agent="myGeocoder")

@app.route('/')
def index():
    # Dùng geopy để tìm tọa độ của "Phường Láng Thượng, Đống Đa, Hà Nội"
    location = geolocator.geocode("Phường Láng Thượng, Đống Đa, Hà Nội")

    if location:
        lat, lon = location.latitude, location.longitude
    else:
        lat, lon = 21.0225, 105.8494  # Hà Nội, mặc định nếu không tìm thấy

    # Tạo bản đồ Folium với tọa độ đã tìm
    m = folium.Map(location=[lat, lon], zoom_start=15)

    # Thêm marker vào bản đồ tại tọa độ
    folium.Marker([lat, lon], popup="Phường Láng Thượng, Đống Đa, Hà Nội").add_to(m)

    # Lưu bản đồ vào một file HTML
    m.save('templates/map.html')

    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
