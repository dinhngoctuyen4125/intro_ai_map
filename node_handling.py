from shapely.geometry import LineString

# Tìm điểm trên các đường đi mà gần điểm clicked vào nhất
def find_nearest_edge(G, point):
    min_dist = float("inf")
    nearest = None
    for u, v, data in G.edges(data=True):
        geom = data.get("geometry", LineString([(G.nodes[u]["x"], G.nodes[u]["y"]),
                                                (G.nodes[v]["x"], G.nodes[v]["y"])]))
        dist = geom.distance(point)
        if dist < min_dist:
            min_dist = dist
            nearest = (u, v, data, geom)
    return nearest

def delete_edges(G, u, v, data):
    if G.has_edge(u, v):
        for key in list(G[u][v].keys()):
            if data == G[u][v][key]:
                G.remove_edge(u, v, key)
                break
    if G.has_edge(v, u):
        for key in list(G[v][u].keys()):
            if data == G[v][u][key]:
                G.remove_edge(v, u, key)
                break

# Nếu nearest không phải đầu mút 2 đoạn thẳng nào cả -> tạo node & edge mới
def add_node_on_edge(G, u, v, data, geom, point):
    # Tính vị trí gần nhất trên cạnh
    projected_point = geom.interpolate(geom.project(point))
    new_x, new_y = projected_point.x, projected_point.y

    # Thêm node mới
    new_node_id = max(G.nodes) + 1
    G.add_node(new_node_id, x=new_x, y=new_y)

    # Tạo hai cạnh mới
    length1 = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (new_x, new_y)]).length
    length2 = LineString([(new_x, new_y), (G.nodes[v]["x"], G.nodes[v]["y"])]).length

    attrs = {k: v for k, v in data.items() if k not in ("geometry", "length")}
    
    G.add_edge(u, new_node_id, length=length1, geometry=LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (new_x, new_y)]), **attrs)
    G.add_edge(new_node_id, v, length=length2, geometry=LineString([(new_x, new_y), (G.nodes[v]["x"], G.nodes[v]["y"])]), **attrs)


    # Nếu đường không một chiều, thêm chiều ngược lại
    if not data.get('oneway', False):
        G.add_edge(new_node_id, u, length=length1, geometry=LineString([(new_x, new_y), (G.nodes[u]["x"], G.nodes[u]["y"])]), **attrs)
        G.add_edge(v, new_node_id, length=length2, geometry=LineString([(G.nodes[v]["x"], G.nodes[v]["y"]), (new_x, new_y)]), **attrs)

    delete_edges(G, u, v, data)

    return new_node_id