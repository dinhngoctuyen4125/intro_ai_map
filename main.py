import osmnx as ox
import matplotlib.pyplot as plt
import contextily as ctx
import networkx as nx
from shapely.geometry import Point

import node_handling, path_handling, a_star, dijkstra

# Giải thích module:
# node_handling: xử lí thêm node, thêm/xóa cạnh
# path_handling: tính toán độ dài đường đi
# a_star: thuật toán A*
# dijkstra: thuật toán Dijkstra

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

    clicked_points = []
    plotted_objects = []
    plotted_user_deleted_edges = {}
    plotted_user_reversed_edges = {}
    coords = []
    path = None

    def on_click(event):
        if event.inaxes != ax:
            return

        x, y = event.xdata, event.ydata
        click_point = Point(x, y)

        if event.button == 3 and 'shift' in event.modifiers: # Shift + Chuột phải: Đảo chiều đường một chiều
            u, v, data, geom = node_handling.find_nearest_edge(G, click_point)

            if data["oneway"] == False or data["oneway"] == "False":
                print("Đường đã chọn không phải đường một chiều")
                print('--------------------------------------------')
                return

            x_start, y_start = G.nodes[u]['x'], G.nodes[u]['y']
            x_end, y_end = G.nodes[v]['x'], G.nodes[v]['y']

            for key in list(G[u][v].keys()):
                if data == G[u][v][key]:
                    G.remove_edge(u, v, key)
                    break
            G.add_edge(v, u, **node_handling.reverse_edge_data(data))

            if (data["reversed"] == "False" or data["reversed"] == False):
                edge = str((u, v, data.copy()))
            else:
                edge = str((v, u, node_handling.reverse_edge_data(data)))

            if not edge in plotted_user_reversed_edges:
                line = ax.plot([x_start, x_end], [y_start, y_end], color='yellow', linewidth=2)[0]
                plotted_user_reversed_edges[edge] = line
            else:
                plotted_user_reversed_edges[edge].remove()
                del plotted_user_reversed_edges[edge]
            
            fig.canvas.draw()  

        elif event.button == 3:  # Chuột phải: xóa cạnh gần nhất
            u, v, data, geom = node_handling.find_nearest_edge(G, click_point)

            if data['reversed'] == True or data['reversed'] == "True":
                u, v = v, u
                data = node_handling.reverse_edge_data(data)

            x_start, y_start = G.nodes[u]['x'], G.nodes[u]['y']
            x_end, y_end = G.nodes[v]['x'], G.nodes[v]['y']

            edge = str((u, v, data.copy()))

            node_handling.delete_edges(G, u, v, data, 2)

            if not edge in plotted_user_deleted_edges:
                line = ax.plot([x_start, x_end], [y_start, y_end], color='red', linewidth=2)[0]
                plotted_user_deleted_edges[edge] = line
            else:
                plotted_user_deleted_edges[edge].remove()
                del plotted_user_deleted_edges[edge]
            
            fig.canvas.draw()  
                


        elif event.button == 1:  # Chuột trái: thêm điểm bắt đầu/kết thúc

            if len(clicked_points) >= 2:
                # Reset khi click lần thứ 3
                restore_graph(G)
                clear_plot()
                return

            clicked_points.append((x, y))

            u, v, data, geom = node_handling.find_nearest_edge(G, click_point)
            new_node = node_handling.add_node_on_edge(G, u, v, data, geom, click_point)

            # Vẽ điểm click đỏ
            point_red = ax.plot(x, y, 'ro')[0]
            plotted_objects.append(point_red)

            # Vẽ điểm node mới xanh
            point_blue = ax.plot(G.nodes[new_node]['x'], G.nodes[new_node]['y'], 'bo')[0]
            plotted_objects.append(point_blue)

            coords.append(new_node)
            fig.canvas.draw()

            if len(clicked_points) == 2:
                find_and_draw_path()

    def restore_graph(G):
        # Khôi phục các cạnh đã xóa và cập nhật các cạnh thêm/xóa người dùng
        for u, v, key, data in node_handling.deleted_edges:
            G.add_edge(u, v, key=key, **data)
        node_handling.deleted_edges.clear()

        for u, v, key, data in node_handling.added_edges:
            if data == G[u][v][key]:
                if (u, v, data) in node_handling.user_deleted_edges:
                    node_handling.user_deleted_edges.remove((u, v, data))
                G.remove_edge(u, v, key)
        node_handling.added_edges.clear()

    def clear_plot():
        nonlocal clicked_points, coords, plotted_objects
        for obj in plotted_objects:
            obj.remove()
        plotted_objects.clear()
        clicked_points.clear()
        coords.clear()
        fig.canvas.draw()

    def find_and_draw_path():
        nonlocal path
        node_start, node_end = coords[0], coords[1]

        print(f"Tọa độ bắt đầu: ({G.nodes[node_start]['x']:.4f}, {G.nodes[node_start]['y']:.4f})")
        print(f"Tọa độ kết thúc: ({G.nodes[node_end]['x']:.4f}, {G.nodes[node_end]['y']:.4f})")

        try:
            if algo == 1:
                path = a_star.heuristic(G, node_start, node_end)
            else:
                path = dijkstra.heuristic(G, node_start, node_end)

            length = path_handling.do_dai_duong_di(G, path)
            print(f'Độ dài đường: {length:.2f} km')
            print('--------------------------------------------')

        except Exception:
            print("Không có đường đi giữa hai điểm đã chọn.")
            print('--------------------------------------------')
            return

        x_route, y_route = zip(*[(G.nodes[n]['x'], G.nodes[n]['y']) for n in path])
        line = ax.plot(x_route, y_route, color='blue', linewidth=2, alpha=0.7)[0]
        plotted_objects.append(line)
        fig.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()


if __name__ == "__main__":
    main()