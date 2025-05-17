import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point

import normal_click, reverse_clicked_edges, delete_clicked_edges, switch_oneway_twoway_clicked_edges

# Giải thích module:
# normal_click: Xử lý với lệnh click trái tìm đường
# delete_edges: Xử lý với lệnh xóa cạnh
# reverse_edges: Xử lý với lệnh đảo chiều đường một chiều

def main():
    print("Chọn thuật toán tìm đường ngắn nhất: [1]: A-star, [2]: Dijkstra")
    algo = int(input())
    if algo == 1:
        print('Thuật toán tìm đường đi ngắn nhất A*')
    else:
        print('Thuật toán tìm đường đi ngắn nhất Dijkstra')
    print('--------------------------------------------')

    place_name = 'Phường Láng Thượng, Đống Đa, Hà Nội'

    # Tải dữ liệu bản đồ
    try:
        G = ox.load_graphml("lang_thuong.graphml")
    except FileNotFoundError:
        G = ox.graph_from_place(place_name, network_type="all")
        ox.save_graphml(G, filepath="lang_thuong.graphml")

    gdf_edges = ox.graph_to_gdfs(G, nodes=False)

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_edges.plot(ax=ax, linewidth=0, edgecolor='blue')
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_edges.crs.to_string())

    def on_click(event):
        if event.inaxes != ax:
            return

        x, y = event.xdata, event.ydata
        click_point = Point(x, y)

        if event.button == 3 and 'shift' in event.modifiers: # Shift + Chuột phải: Đảo chiều đường một chiều
            reverse_clicked_edges.process(G, fig, ax, click_point)
            return
        
        if event.button == 3 and 'ctrl' in event.modifiers: #Ctrl + Chuột phải: Chuyển 1 chiều thành 2 chiều và ngược lại
            switch_oneway_twoway_clicked_edges.process(G, fig, ax, click_point)
            return

        if event.button == 3:  # Chuột phải: xóa cạnh gần nhất
            delete_clicked_edges.process(G, fig, ax, click_point)
            return

        if event.button == 1:  # Chuột trái: thêm điểm bắt đầu/kết thúc
            normal_click.process(G, fig, ax, click_point, algo)
            return 

    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()


if __name__ == "__main__":
    main()