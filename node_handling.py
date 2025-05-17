from shapely.geometry import LineString
import copy
import delete_clicked_edges

deleted_edges = [] # Cạnh bị xóa khi tách cạnh
added_edges = [] # Cạnh sau khi tách được lưu lại

def last_edge(G, u, v): # Lấy cạnh cuối cùng từ u đến v
    key = max(G[u][v].keys())
    data = G[u][v][key].copy()
    return (u, v, key, data)

def find_nearest_edge(G, point): # Tìm cạnh gần điểm nhất
    min_dist = float("inf")
    nearest = None
    for u, v, data in G.edges(data=True):
        geom = data.get("geometry", LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]))
        dist = geom.distance(point)
        if dist < min_dist:
            min_dist = dist
            nearest = (u, v, data, geom)
    return nearest

def reverse_edge_data(data): # Đảo ngược data cạnh
    # Tạo bản sao sâu để tránh thay đổi gốc
    new_data = copy.deepcopy(data)

    # Đảo ngược geometry nếu có
    if "geometry" in new_data:
        new_data["geometry"] = LineString(list(new_data["geometry"].coords)[::-1])
    
    # Đảo ngược trường 'reversed' nếu có
    if "reversed" in new_data:
        if isinstance(new_data["reversed"], str):  # nếu là chuỗi "True"/"False"
            new_data["reversed"] = "False" if new_data["reversed"] == "True" else "True"
        elif isinstance(new_data["reversed"], bool):
            new_data["reversed"] = not new_data["reversed"]
    
    return new_data

def delete_edges(G, u, v, data, switched = 0): # Xóa 1 cạnh (cả 2 chiều nếu có)
    if G.has_edge(u, v):
        for key in list(G[u][v].keys()):
            if data == G[u][v][key]:
                deleted_edges.append((u, v, key, data.copy()))
                G.remove_edge(u, v, key)
                break

    if switched == 0 and G.has_edge(v, u):
        delete_edges(G, v, u, reverse_edge_data(data), 1)

def add_edge(G, u, v, data): # Thêm 1 cạnh 1 chiều từ u đến v
    line = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])])
    length = line.length * 100000
    attrs = {k: v for k, v in data.items() if k not in ("geometry", "length")}
    G.add_edge(u, v, length=length, geometry=line, **attrs)
    added_edges.append(last_edge(G, u, v))

def add_two_edges(G, u, v, new_node, data, switched = 0): # Thêm 2 cạnh u->new, new->v và cả new->u, v->new nếu u->v hai chiều
    add_edge(G, u, new_node, data)
    add_edge(G, new_node, v, data)

    if (u, v, data) in delete_clicked_edges.deleted_edges:
        delete_clicked_edges.delete_last_edge(G, u, new_node)
        delete_clicked_edges.delete_last_edge(G, new_node, v)
    
    # Nếu đường hai chiều, thêm chiều ngược lại
    if switched == 0 and not data.get('oneway', True):
        add_two_edges(G, v, u, new_node, reverse_edge_data(data), 1)

def add_node_on_edge(G, u, v, data, geom, point): #Tìm điểm trên u->v gần nhất với point và tách u->v thành 2 cạnh (tách cả v->u nếu 2 chiều)
    # Tính vị trí gần nhất trên cạnh
    projected_point = geom.interpolate(geom.project(point))
    new_x, new_y = projected_point.x, projected_point.y

    # Thêm node mới
    new_node_id = max(G.nodes) + 1
    G.add_node(new_node_id, x=new_x, y=new_y)

    add_two_edges(G, u, v, new_node_id, data)

    delete_edges(G, u, v, data)
    return new_node_id