import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
import networkx as nx
from shapely.geometry import Point, LineString

import heuristic

print("Choose algorithm for finding shortest path: [1]: A-star, [2]: Dijkstra")
algo = int(input())

if algo == 1:
    print('Thuật toán tìm đường đi ngắn nhất A*')
else:
    print('Thuật toán tìm đường đi ngắn nhất Dijkstra')

print('--------------------------------------------')

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


def find_nearest_edge(G, point):
    min_dist = float("inf")
    nearest = None
    for u, v, data in G.edges(data=True):
        geom = data.get("geometry", LineString([(G.nodes[u]["x"], G.nodes[u]["y"]),
                                                (G.nodes[v]["x"], G.nodes[v]["y"])]))
        dist = geom.distance(point)
        if dist < min_dist:
            min_dist = dist
            nearest = (u, v, data, geom)
    return nearest

def add_node_on_edge(G, u, v, data, geom, point):
    # Tính vị trí gần nhất trên cạnh
    projected_point = geom.interpolate(geom.project(point))
    new_x, new_y = projected_point.x, projected_point.y

    # Thêm node mới
    new_node_id = max(G.nodes) + 1
    G.add_node(new_node_id, x=new_x, y=new_y)

    # Tạo hai cạnh mới
    length1 = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (new_x, new_y)]).length
    length2 = LineString([(new_x, new_y), (G.nodes[v]["x"], G.nodes[v]["y"])]).length

    attrs = {k: v for k, v in data.items() if k not in ("geometry", "length")}
    G.add_edge(u, new_node_id, length=length1, geometry=LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (new_x, new_y)]), **attrs)
    G.add_edge(new_node_id, u, length=length1, geometry=LineString([(new_x, new_y), (G.nodes[u]["x"], G.nodes[u]["y"])]), **attrs)

    G.add_edge(new_node_id, v, length=length2, geometry=LineString([(new_x, new_y), (G.nodes[v]["x"], G.nodes[v]["y"])]), **attrs)
    G.add_edge(v, new_node_id, length=length2, geometry=LineString([(G.nodes[v]["x"], G.nodes[v]["y"]), (new_x, new_y)]), **attrs)


    # Xóa cạnh cũ
    if G.is_multigraph():
        keys = list(G[u][v].keys())
        for k in keys:
            if G[u][v][k] == data:
                G.remove_edge(u, v, key=k)
    else:
        G.remove_edge(u, v)

    return new_node_id





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

    
    click_point = Point(x, y)
    u, v, data, geom = find_nearest_edge(G, click_point)
    new_node = add_node_on_edge(G, u, v, data, geom, click_point)
    point = ax.plot(x, y, 'bo')[0]
    plotted_objects.append(point)
    fig.canvas.draw()
    
    point = ax.plot(G.nodes[new_node]['x'], G.nodes[new_node]['y'], 'ro')[0]
    plotted_objects.append(point)
    coords.append(new_node)


    
    # Tô đỏ điểm vừa click
    

    # nearest_node = ox.distance.nearest_nodes(G, x, y)
    

    fig.canvas.draw()

    # Click đủ 2 lần thì tìm đường đi, vẽ đường đi,... thôi
    if len(clicked_points) == 2:

        node_start = coords[0]
        node_end = coords[1]

        print(f"Tọa độ bắt đầu: ({G.nodes[node_start]['x']:.4f}, {G.nodes[node_start]['y']:.4f})")
        print(f"Tọa độ kết thúc: ({G.nodes[node_end]['x']:.4f}, {G.nodes[node_end]['y']:.4f})")
        
        try:
            if (algo == 1):
                path = heuristic.a_star(G, node_start, node_end)
            
            else:
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
        
        print('--------------------------------------------')


cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()