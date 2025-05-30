import node_handling, reverse_clicked_edges
import copy

plotted_edges = [{}, {}] #0: oneway, 1: twoway

def switch_oneway_twoway_data(data): # Đảo giá trị oneway của data
    # Tạo bản sao sâu để tránh thay đổi gốc
    new_data = copy.deepcopy(data)

    if isinstance(new_data["oneway"], str):  # nếu là chuỗi "True"/"False"
        new_data["oneway"] = "False" if new_data["oneway"] == "True" else "True"
    elif isinstance(new_data["oneway"], bool):
        new_data["oneway"] = not new_data["oneway"]
    return new_data

def delete_edge_from_graph(G, u, v, data):
    if not G.has_edge(u, v): return
    for key in list(G[u][v].keys()):
        if str(data) == str(G[u][v][key]):
            G.remove_edge(u, v, key)
            break

def process(G, fig, ax, point):
    u, v, data, geom = node_handling.find_nearest_edge(G, point)
    rdata = node_handling.reverse_edge_data(data)
    ndata = switch_oneway_twoway_data(data)
    rndata = node_handling.reverse_edge_data(ndata)

    x_start, y_start = G.nodes[u]['x'], G.nodes[u]['y']
    x_end, y_end = G.nodes[v]['x'], G.nodes[v]['y']

    if data["reversed"] == "False" or data["reversed"] == False:
        U, V, DATA, nDATA = u, v, copy.deepcopy(data), copy.deepcopy(ndata)
    else:
        U, V, DATA, nDATA = v, u, copy.deepcopy(rdata), copy.deepcopy(rndata)

    delete_edge_from_graph(G, u, v, data)

    if data["oneway"] == False or data["oneway"] == "False":
        mode = 0
        delete_edge_from_graph(G, v, u, rdata)
        if not str((U, V, DATA)) in reverse_clicked_edges.plotted_reversed_edges:
            G.add_edge(U, V, **nDATA)
        else:
            G.add_edge(V, U, **node_handling.reverse_edge_data(nDATA))
    else:
        mode = 1
        G.add_edge(u, v, **ndata)
        G.add_edge(v, u, **rndata)

    if not str((U, V, DATA)) in plotted_edges[1 - mode]:
        line = ax.plot([x_start, x_end], [y_start, y_end], color='green' if mode == 0 else 'purple', linewidth=2)[0]
        plotted_edges[mode][str((U, V, nDATA))] = line
    else:
        plotted_edges[1 - mode][str((U, V, DATA))].remove()
        del plotted_edges[1 - mode][str((U, V, DATA))]
    
    fig.canvas.draw()  