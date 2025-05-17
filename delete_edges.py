import node_handling

plotted_user_deleted_edges = {}

def delete_edge(G, fig, ax, point):
    u, v, data, geom = node_handling.find_nearest_edge(G, point)

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