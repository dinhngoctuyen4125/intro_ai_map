import node_handling

deleted_edges = [] # Cạnh do người dùng xóa (cạnh đỏ)

plotted_deleted_edges = {} 

def delete_last_edge(G, u, v): # Xóa cạnh cuối cùng u->v
    edge = node_handling.last_edge(G, u, v)
    deleted_edges.append(edge[0:2] + edge[3:4])

def delete_edges(G, u, v, data, switched = 0): # Xóa 1 cạnh (cả 2 chiều nếu có)
    global deleted_edges
    if G.has_edge(u, v):
        for key in list(G[u][v].keys()):
            if data == G[u][v][key]:
                if not str((u, v, data.copy())) in map(str, deleted_edges):
                    deleted_edges.append((u, v, data.copy()))
                else:
                    deleted_edges = [item for item in deleted_edges if str(item) != str((u, v, data.copy()))]
                break

    if switched == 0 and G.has_edge(v, u):
        delete_edges(G, v, u, node_handling.reverse_edge_data(data), 1)

def process(G, fig, ax, point):
    u, v, data, geom = node_handling.find_nearest_edge(G, point)

    if data['reversed'] == True or data['reversed'] == "True":
        u, v = v, u
        data = node_handling.reverse_edge_data(data)

    x_start, y_start = G.nodes[u]['x'], G.nodes[u]['y']
    x_end, y_end = G.nodes[v]['x'], G.nodes[v]['y']

    edge = str((u, v, data.copy()))

    delete_edges(G, u, v, data)

    if not edge in plotted_deleted_edges:
        line = ax.plot([x_start, x_end], [y_start, y_end], color='red', linewidth=2)[0]
        plotted_deleted_edges[edge] = line
    else:
        plotted_deleted_edges[edge].remove()
        del plotted_deleted_edges[edge]
    
    fig.canvas.draw()  