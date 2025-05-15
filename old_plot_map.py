import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
import networkx as nx
from shapely.geometry import Point

import heuristic

# Tải graph từ khu vực
place_name = 'Phường Láng Thượng, Đống Đa, Hà Nội'

try:
    G = ox.load_graphml("lang_thuong.graphml")
except:
    G = ox.graph_from_place(place_name, network_type="all")
    ox.save_graphml(G, filepath="lang_thuong.graphml")

# Chuyển sang GeoDataFrame
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

# Vẽ bằng matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
gdf_edges.plot(ax=ax, linewidth=0, edgecolor='blue')

# Thêm lớp nền bản đồ thật (tile màu)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_edges.crs.to_string())

clicked_points = []
plotted_objects = []

def on_click(event):
    if event.inaxes != ax:
        return

    global clicked_points, plotted_objects

    # Nếu đã click 2 điểm rồi → lần thứ 3 → reset
    if len(clicked_points) >= 2:
        # Xóa các đối tượng cũ (nút và đường)
        for obj in plotted_objects:
            obj.remove()
        plotted_objects.clear()
        clicked_points.clear()
        fig.canvas.draw()
        return

    # Lưu điểm click
    x, y = event.xdata, event.ydata
    clicked_points.append((x, y))

    # Vẽ điểm đỏ
    point = ax.plot(x, y, 'ro')[0]
    plotted_objects.append(point)
    fig.canvas.draw()

    if len(clicked_points) == 2:
        # Tìm node gần nhất
        (x1, y1), (x2, y2) = clicked_points
        node_start = ox.distance.nearest_nodes(G, x1, y1)
        node_end = ox.distance.nearest_nodes(G, x2, y2)

        print(f"Tọa độ bắt đầu: {G.nodes[node_start]['x'], G.nodes[node_start]['y']}")
        print(f"Tọa độ kết thúc: {G.nodes[node_end]['x'], G.nodes[node_end]['y']}")
        

        # Kiểm tra nếu không có đường đi
        try:
            # path = nx.shortest_path(G, node_start, node_end, weight="length")
            
            path = heuristic.dijkstra(G, node_start, node_end)
            # path = heuristic.a_star(G, node_start, node_end)

        except nx.NetworkXNoPath:
            print("Không có đường đi giữa hai điểm đã chọn.")
            return
        
        print(f'Dãy các điểm đi qua: {path}')

        # Vẽ đường đi ngắn nhất
        x_route, y_route = zip(*[(G.nodes[n]['x'], G.nodes[n]['y']) for n in path])
        line = ax.plot(x_route, y_route, color='red', linewidth=2, alpha=0.7)[0]
        plotted_objects.append(line)
        fig.canvas.draw()
        
        print('-----------')


cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()