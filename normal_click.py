import node_handling, delete_clicked_edges, distance, shortest_path

clicked_points = []
plotted_objects = []
coords = []
path = None

def process(G, fig, ax, point, algo):
    if len(clicked_points) >= 2:
        # Reset khi click lần thứ 3
        restore_graph(G)
        clear_plot(fig)
        return

    x, y = point.x, point.y
    clicked_points.append((x, y))

    u, v, data, geom = node_handling.find_nearest_edge(G, point)
    new_node = node_handling.add_node_on_edge(G, u, v, data, geom, point)

    # Vẽ điểm click đỏ
    point_red = ax.plot(x, y, 'ro')[0]
    plotted_objects.append(point_red)

    # Vẽ điểm node mới xanh
    point_blue = ax.plot(G.nodes[new_node]['x'], G.nodes[new_node]['y'], 'bo')[0]
    plotted_objects.append(point_blue)

    coords.append(new_node)
    fig.canvas.draw()

    if len(clicked_points) == 2:
        find_and_draw_path(G, fig, ax, algo)


def restore_graph(G):
    # Khôi phục các cạnh đã xóa và cập nhật các cạnh thêm/xóa người dùng
    for u, v, key, data in node_handling.deleted_edges:
        G.add_edge(u, v, key=key, **data)
    node_handling.deleted_edges.clear()

    for u, v, key, data in node_handling.added_edges:
        if data == G[u][v][key]:
            delete_clicked_edges.deleted_edges = [item for item in delete_clicked_edges.deleted_edges if str(item) != str((u, v, data.copy()))]
            G.remove_edge(u, v, key)
    node_handling.added_edges.clear()

def clear_plot(fig):
    # nonlocal clicked_points, coords, plotted_objects
    for obj in plotted_objects:
        obj.remove()
    plotted_objects.clear()
    clicked_points.clear()
    coords.clear()
    fig.canvas.draw()

def find_and_draw_path(G, fig, ax, algo):
    # nonlocal path
    node_start, node_end = coords[0], coords[1]

    print(f"Tọa độ bắt đầu: ({G.nodes[node_start]['x']:.4f}, {G.nodes[node_start]['y']:.4f})")
    print(f"Tọa độ kết thúc: ({G.nodes[node_end]['x']:.4f}, {G.nodes[node_end]['y']:.4f})")

    try:
        if algo == 1:
            path = shortest_path.a_star(G, node_start, node_end)
        else:
            path = shortest_path.dijkstra(G, node_start, node_end)

        length = distance.do_dai_duong_di(G, path)
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