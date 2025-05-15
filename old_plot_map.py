import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
import networkx as nx
from shapely.geometry import Point

import heuristic

print("Choose algorithm for finding shortest path: [1]: A-star, [2]: Dijkstra")
algo = int(input())

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

clicked_points = [] # Các điểm đã click trên màn hình
plotted_objects = [] # Các đối tượng vẽ ra màn hình (điểm, đường thẳng,...)
coords = []
path = None

def on_click(event):
    # Nếu on_click không trong bản đồ thì bỏ qua
    if event.inaxes != ax:
        return

    # Nếu click đến lần thứ 3 thì xóa đi
    if len(clicked_points) >= 2:
        # Xóa các đối tượng cũ (nút và đường)
        for obj in plotted_objects:
            obj.remove()
        
        coords.clear()
        plotted_objects.clear()
        clicked_points.clear()
        fig.canvas.draw()
        return

    # Lưu lại các điểm click
    x, y = event.xdata, event.ydata
    clicked_points.append((x, y))

    # Tô đỏ điểm vừa click
    point = ax.plot(x, y, 'bo')[0]
    plotted_objects.append(point)

    nearest_node = ox.distance.nearest_nodes(G, x, y)
    point = ax.plot(G.nodes[nearest_node]['x'], G.nodes[nearest_node]['y'], 'ro')[0]
    plotted_objects.append(point)
    coords.append(nearest_node)

    fig.canvas.draw()

    # Click đủ 2 lần thì tìm đường đi, vẽ đường đi,... thôi
    if len(clicked_points) == 2:

        node_start = coords[0]
        node_end = coords[1]

        print(f"Tọa độ bắt đầu: {G.nodes[node_start]['x'], G.nodes[node_start]['y']}")
        print(f"Tọa độ kết thúc: {G.nodes[node_end]['x'], G.nodes[node_end]['y']}")
        
        try:
            if (algo == 1):
                print('Thuật toán A*')
                path = heuristic.a_star(G, node_start, node_end)
            
            else:
                print('Thuật toán Dijkstra')
                path = heuristic.dijkstra(G, node_start, node_end)
            
            print(f'Độ dài đường: {heuristic.do_dai_duong_di(G, path):.2f} km')

        except nx.NetworkXNoPath:
            print("Không có đường đi giữa hai điểm đã chọn.")
            return

        # Vẽ đường đi ngắn nhất
        x_route, y_route = zip(*[(G.nodes[n]['x'], G.nodes[n]['y']) for n in path])
        line = ax.plot(x_route, y_route, color='red', linewidth=2, alpha=0.7)[0]
        plotted_objects.append(line)
        fig.canvas.draw()
        
        print('-----------')


cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()