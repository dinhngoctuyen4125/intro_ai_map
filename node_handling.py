from shapely.geometry import LineString
import copy

user_deleted_edges = []
deleted_edges = []
added_edges = []

def save_last_added_edge(G, u, v):
    key = max(G[u][v].keys())
    data = G[u][v][key].copy()
    return (u, v, key, data)

# Tìm điểm trên các đường đi mà gần điểm clicked vào nhất
def find_nearest_edge(G, point):
    min_dist = float("inf")
    nearest = None
    for u, v, data in G.edges(data=True):
        geom = data.get("geometry", LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]))
        dist = geom.distance(point)
        if dist < min_dist:
            min_dist = dist
            nearest = (u, v, data, geom)
    return nearest

def reverse_edge_data(data):
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

def delete_edges(G, u, v, data, mode = 1):
    if G.has_edge(u, v):
        for key in list(G[u][v].keys()):
            if data == G[u][v][key]:
                if mode == 1: 
                    deleted_edges.append((u, v, key, data.copy()))
                    G.remove_edge(u, v, key)
                else:
                    user_deleted_edges.append((u, v, data.copy()))
                    print (user_deleted_edges)
                break

    new_data = reverse_edge_data(data)
    if G.has_edge(v, u):
        for key in list(G[v][u].keys()):
            if new_data == G[v][u][key]:
                if mode == 1:
                    deleted_edges.append((v, u, key, new_data))
                    G.remove_edge(v, u, key)
                else:
                    user_deleted_edges.append((v, u, new_data))
                    print(user_deleted_edges)
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
    line1 = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (new_x, new_y)])
    line2 = LineString([(new_x, new_y), (G.nodes[v]["x"], G.nodes[v]["y"])])
    length1 = line1.length * 100000
    length2 = line2.length * 100000
    attrs = {k: v for k, v in data.items() if k not in ("geometry", "length")}
    
    G.add_edge(u, new_node_id, length=length1, geometry=line1, **attrs)
    added_edges.append(save_last_added_edge(G, u, new_node_id))
    G.add_edge(new_node_id, v, length=length2, geometry=line2, **attrs)
    added_edges.append(save_last_added_edge(G, new_node_id, v))
    if (u, v, data) in user_deleted_edges:
        edge1 = save_last_added_edge(G, u, new_node_id)
        user_deleted_edges.append(edge1[0:2] + edge1[3:4])
        edge2 = save_last_added_edge(G, new_node_id, v)
        user_deleted_edges.append(edge2[0:2] + edge2[3:4])
        print(user_deleted_edges)
    

    # Nếu đường hai chiều, thêm chiều ngược lại
    if not data.get('oneway', True):
        data2 = reverse_edge_data(data)
        attrs2 = {k: v for k, v in data2.items() if k not in ("geometry", "length")}

        line3 = LineString([(new_x, new_y), (G.nodes[u]["x"], G.nodes[u]["y"])])
        line4 = LineString([(G.nodes[v]["x"], G.nodes[v]["y"]), (new_x, new_y)])
        G.add_edge(new_node_id, u, length=length1, geometry=line3, **attrs2)
        added_edges.append(save_last_added_edge(G, new_node_id, u))
        G.add_edge(v, new_node_id, length=length2, geometry=line4, **attrs2)
        added_edges.append(save_last_added_edge(G, v, new_node_id))

        if (v, u, data2) in user_deleted_edges:
            edge1 = save_last_added_edge(G, new_node_id, u)
            user_deleted_edges.append(edge1[0:2] + edge1[3:4])
            edge2 = save_last_added_edge(G, v, new_node_id)
            user_deleted_edges.append(edge2[0:2] + edge2[3:4])
            print(user_deleted_edges)

    delete_edges(G, u, v, data)

    return new_node_id

def same_edge(e1, e2):
    u1, v1, d1 = e1
    u2, v2, d2 = e2

    if u1 != u2 or v1 != v2:
        return False

    for k in d1:
        if k not in d2:
            return False
        if k == 'geometry':
            if not d1[k].equals(d2[k]):
                return False
        else:
            if d1[k] != d2[k]:
                return False

    return True