import math

# Khoảng cách thực tế giữa 2 vị trí dựa trên kinh độ & vĩ độ
def distance_on_earth(G, node1, node2):
    # (lon, lat): (kinh độ, vĩ độ)
    lon1, lat1 = G.nodes[node1]['x'], G.nodes[node1]['y']
    lon2, lat2 = G.nodes[node2]['x'], G.nodes[node2]['y']

    avg_lat_rad = math.radians((lat1 + lat2) / 2)
    x = (lon2 - lon1) * 111 * math.cos(avg_lat_rad)
    y = (lat2 - lat1) * 111
    d = math.sqrt(x**2 + y**2)
    return d # đơn vị: km

# Độ dài đường đi ngắn nhất
def do_dai_duong_di(G, path):
    cal = 0
    for i in range(1, len(path)):
        cal += distance_on_earth(G, path[i - 1], path[i])
    
    return cal