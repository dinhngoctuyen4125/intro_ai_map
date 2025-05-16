import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
import networkx as nx
from shapely.geometry import Point

import node_handling, path_handling, a_star, dijkstra
# node_handling: xử lí thêm node, thêm cạnh, xóa cạnh mới
# path_handling: tính toán độ dài đường đi tìm được
# a_star: thuật toán a*
# dijkstra: thuật toán dijkstra

print("Choose algorithm for finding shortest path: [1]: A-star, [2]: Dijkstra")
algo = int(input())
if algo == 1:
    print('Thuật toán tìm đường đi ngắn nhất A*')
else:
    print('Thuật toán tìm đường đi ngắn nhất Dijkstra')
print('--------------------------------------------')

# Tải dữ liệu bản đồ của khu vực, lưu vào trong lang_thuong.graphml
place_name = 'Phường Láng Thượng, Đống Đa, Hà Nội'

try:
    G = ox.load_graphml("lang_thuong.graphml")
except:
    # nếu như chưa có thì sẽ lấy từ trên mạng về, sau đó lưu file mới
    G = ox.graph_from_place(place_name, network_type="all")
    ox.save_graphml(G, filepath="lang_thuong.graphml")

# Chuyển sang GeoDataFrame
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

# Vẽ bản đồ bằng công cụ matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
gdf_edges.plot(ax=ax, linewidth=0, edgecolor='blue')

# Thêm lớp nền cho bản đồ có màu sắc, nền đường, ao hồ, nước,...
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_edges.crs.to_string())

clicked_points = [] # Các điểm đã click trên màn hình
plotted_objects = [] # Các đối tượng vẽ ra màn hình (điểm, đường thẳng,...)
coords = [] # lưu 2 tọa độ là bắt đầu và kết thúc
path = None # đường đi start -> end đi qua những đỉnh nào

def on_click(event):
    # Nếu on_click không trong bản đồ thì bỏ qua
    if event.inaxes != ax:
        return
    x, y = event.xdata, event.ydata
    click_point = Point(x, y)

    # Xử lí chuột phải
    if event.button == 3:
        u, v, data, geom = node_handling.find_nearest_edge(G, click_point)

        x_start = G.nodes[u]['x']
        y_start = G.nodes[u]['y']
        x_end = G.nodes[v]['x']
        y_end = G.nodes[v]['y']

        line = ax.plot([x_start, x_end], [y_start, y_end], color='red', linewidth=2)[0]
        # plotted_objects.append(line)
        fig.canvas.draw()

        node_handling.delete_edges(G, u, v, data, 2)

    elif event.button == 1:
        # Nếu click đến lần thứ 3 thì xóa đi
        if len(clicked_points) >= 2:
            for (u, v, key, data) in node_handling.deleted_edges:
                G.add_edge(u, v, key=key, **data)
            node_handling.deleted_edges.clear()
            for (u, v, key, data) in node_handling.added_edges:
                if data == G[u][v][key]:
                    if (u, v, data) in node_handling.user_deleted_edges:
                        node_handling.user_deleted_edges.remove((u, v, data))
                    G.remove_edge(u, v, key)
            node_handling.added_edges.clear()

            # Xóa các đối tượng cũ (nút và đường)
            for obj in plotted_objects:
                obj.remove()
            
            coords.clear()
            plotted_objects.clear()
            clicked_points.clear()
            fig.canvas.draw()
            return

        # Lưu lại các điểm click
        clicked_points.append((x, y))
        
        u, v, data, geom = node_handling.find_nearest_edge(G, click_point)
        new_node = node_handling.add_node_on_edge(G, u, v, data, geom, click_point)

        # tô đỏ điểm click (ro -> red)
        point = ax.plot(x, y, 'ro')[0]
        plotted_objects.append(point)
        
        # tô xanh điểm gần nhất vừa tìm (bo -> blue)
        point = ax.plot(G.nodes[new_node]['x'], G.nodes[new_node]['y'], 'bo')[0]
        plotted_objects.append(point)
        coords.append(new_node)
        
        fig.canvas.draw()

        # Click đủ 2 lần thì tìm đường đi, vẽ đường đi,... thôi
        if len(clicked_points) == 2:

            node_start = coords[0]
            node_end = coords[1]

            print(f"Tọa độ bắt đầu: ({G.nodes[node_start]['x']:.4f}, {G.nodes[node_start]['y']:.4f})")
            print(f"Tọa độ kết thúc: ({G.nodes[node_end]['x']:.4f}, {G.nodes[node_end]['y']:.4f})")
            
            try:
                if (algo == 1):
                    path = a_star.heuristic(G, node_start, node_end)
                else:
                    path = dijkstra.heuristic(G, node_start, node_end)
                
                print(f'Độ dài đường: {path_handling.do_dai_duong_di(G, path):.2f} km')
                print('--------------------------------------------')

            except:
                print("Không có đường đi giữa hai điểm đã chọn.")
                print('--------------------------------------------')
                return

            # Vẽ đường đi ngắn nhất (màu đỏ)
            x_route, y_route = zip(*[(G.nodes[n]['x'], G.nodes[n]['y']) for n in path])
            line = ax.plot(x_route, y_route, color='blue', linewidth=2, alpha=0.7)[0]
            plotted_objects.append(line)
            fig.canvas.draw()


cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()