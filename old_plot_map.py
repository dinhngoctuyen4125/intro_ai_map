import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
import networkx as nx
from shapely.geometry import Point

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
fig, ax = plt.subplots(figsize=(13, 13))
gdf_edges.plot(ax=ax, linewidth=1, edgecolor='blue')

# Thêm lớp nền bản đồ thật (tile màu)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_edges.crs.to_string())

clicked_points = []
plotted_objects = []


# # Hàm xử lý click chuột
# def on_click(event):
#     if event.inaxes != ax:
#         return
    
#     if len(clicked_points) >= 2:
#         # Xóa các đối tượng cũ (nút và đường)
#         for obj in plotted_objects:
#             obj.remove()
#         plotted_objects.clear()
#         clicked_points.clear()
#         fig.canvas.draw()
#         return




#     x, y = event.xdata, event.ydata
#     print(f"[CLICK] Projected coords: x={x:.2f}, y={y:.2f}")

#     # Chuyển từ tọa độ projected sang (lon, lat)
#     point_proj = Point(x, y)
#     point_geo = ox.projection.project_geometry(point_proj, crs=gdf_edges.crs, to_latlong=True)[0]
#     lon, lat = point_geo.xy[0][0], point_geo.xy[1][0]
#     print(f"[CONVERTED] lon={lon:.6f}, lat={lat:.6f}")
#     ax.plot(lon, lat, 'bo', markersize=5)

#     # Tìm node gần nhất trong graph
#     node_id = ox.distance.nearest_nodes(G, X=lon, Y=lat)
#     print(f"[NEAREST NODE] ID: {node_id}")

#     # Vẽ node tìm được
#     node_point = G.nodes[node_id]
#     ax.plot(node_point['x'], node_point['y'], 'ro', markersize=8)
#     fig.canvas.draw()


#     clicked_points.append((lon, lat))
#     point = ax.plot(x, y, 'ro')[0]

#     plotted_objects.append(point)


#     if len(clicked_points) == 2:
#         # Tìm node gần nhất
#         (x1, y1), (x2, y2) = clicked_points
#         node_start = ox.distance.nearest_nodes(G, x1, y1)
#         node_end = ox.distance.nearest_nodes(G, x2, y2)

#         # Kiểm tra nếu không có đường đi
#         try:
#             path = nx.shortest_path(G, node_start, node_end, weight="length")
#         except nx.NetworkXNoPath:
#             print("Không có đường đi giữa hai điểm đã chọn.")
#             return

#         # Vẽ đường đi ngắn nhất
#         x_route, y_route = zip(*[(G.nodes[n]['x'], G.nodes[n]['y']) for n in path])
#         line = ax.plot(x_route, y_route, color='red', linewidth=3, alpha=0.7)[0]
#         plotted_objects.append(line)
#         fig.canvas.draw()

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

    if len(clicked_points) == 2:
        # Tìm node gần nhất
        (x1, y1), (x2, y2) = clicked_points
        node_start = ox.distance.nearest_nodes(G, x1, y1)
        node_end = ox.distance.nearest_nodes(G, x2, y2)

        # Kiểm tra nếu không có đường đi
        try:
            path = nx.shortest_path(G, node_start, node_end, weight="length")
        except nx.NetworkXNoPath:
            print("Không có đường đi giữa hai điểm đã chọn.")
            return

        # Vẽ đường đi ngắn nhất
        x_route, y_route = zip(*[(G.nodes[n]['x'], G.nodes[n]['y']) for n in path])
        line = ax.plot(x_route, y_route, color='red', linewidth=3, alpha=0.7)[0]
        plotted_objects.append(line)
        fig.canvas.draw()


cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()