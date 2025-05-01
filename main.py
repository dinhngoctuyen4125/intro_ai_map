import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point


# Tải graph từ khu vực
place_name = 'Phường Láng Thượng, Đống Đa, Hà Nội'
G = ox.graph_from_place(place_name, network_type="all")

# Chuyển sang GeoDataFrame
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

# Vẽ bằng matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
gdf_edges.plot(ax=ax, linewidth=1, edgecolor='blue')

# Thêm lớp nền bản đồ thật (tile màu)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_edges.crs.to_string())

# Hàm xử lý click chuột
def on_click(event):
    if event.inaxes != ax:
        return
    x, y = event.xdata, event.ydata
    print(f"[CLICK] Projected coords: x={x:.2f}, y={y:.2f}")

    # Chuyển từ tọa độ projected sang (lon, lat)
    point_proj = Point(x, y)
    point_geo = ox.projection.project_geometry(point_proj, crs=gdf_edges.crs, to_latlong=True)[0]
    lon, lat = point_geo.xy[0][0], point_geo.xy[1][0]
    print(f"[CONVERTED] lon={lon:.6f}, lat={lat:.6f}")
    ax.plot(lon, lat, 'bo', markersize=5)


    # Tìm node gần nhất trong graph
    node_id = ox.distance.nearest_nodes(G, X=lon, Y=lat)
    print(f"[NEAREST NODE] ID: {node_id}")

    # Vẽ node tìm được
    node_point = G.nodes[node_id]
    ax.plot(node_point['x'], node_point['y'], 'ro', markersize=8)
    fig.canvas.draw()

fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()