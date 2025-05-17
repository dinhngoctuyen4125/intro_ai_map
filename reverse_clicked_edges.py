import node_handling

plotted_reversed_edges = {}

def process(G, fig, ax, point):
    u, v, data, geom = node_handling.find_nearest_edge(G, point)

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

    if not edge in plotted_reversed_edges:
        line = ax.plot([x_start, x_end], [y_start, y_end], color='yellow', linewidth=2)[0]
        plotted_reversed_edges[edge] = line
    else:
        plotted_reversed_edges[edge].remove()
        del plotted_reversed_edges[edge]
    
    fig.canvas.draw()  