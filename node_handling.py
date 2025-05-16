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

def delete_edges(G, u, v, data, mode = 1, switched = 0):
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

    if switched == 0 and G.has_edge(v, u):
        delete_edges(G, v, u, reverse_edge_data(data), mode, 1)

def add_edge(G, u, v, data):
    line = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])])
    length = line.length * 100000
    attrs = {k: v for k, v in data.items() if k not in ("geometry", "length")}
    G.add_edge(u, v, length=length, geometry=line, **attrs)
    added_edges.append(save_last_added_edge(G, u, v))

def add_two_edges(G, u, v, new_node, data, switched = 0):
    add_edge(G, u, new_node, data)
    add_edge(G, new_node, v, data)

    if (u, v, data) in user_deleted_edges:
        user_delete_last_edge(G, u, new_node)
        user_delete_last_edge(G, new_node, v)
        print(user_deleted_edges)
    
    # Nếu đường hai chiều, thêm chiều ngược lại
    if switched == 0 and not data.get('oneway', True):
        add_two_edges(G, v, u, new_node, reverse_edge_data(data), 1)

def user_delete_last_edge(G, u, v):
    edge1 = save_last_added_edge(G, u, v)
    user_deleted_edges.append(edge1[0:2] + edge1[3:4])

# Nếu nearest không phải đầu mút 2 đoạn thẳng nào cả -> tạo node & edge mới
def add_node_on_edge(G, u, v, data, geom, point):
    # Tính vị trí gần nhất trên cạnh
    projected_point = geom.interpolate(geom.project(point))
    new_x, new_y = projected_point.x, projected_point.y

    # Thêm node mới
    new_node_id = max(G.nodes) + 1
    G.add_node(new_node_id, x=new_x, y=new_y)

    add_two_edges(G, u, v, new_node_id, data)

    # add_edge(G, u, new_node_id, data)
    # add_edge(G, new_node_id, v, data)

    # if (u, v, data) in user_deleted_edges:
    #     user_delete_last_edge(G, u, new_node_id)
    #     user_delete_last_edge(G, new_node_id, v)
    #     print(user_deleted_edges)
    
    # # Nếu đường hai chiều, thêm chiều ngược lại
    # if not data.get('oneway', True):
    #     data2 = reverse_edge_data(data)
    #     add_edge(G, new_node_id, u, data2)
    #     add_edge(G, v, new_node_id, data2)

    #     if (v, u, data2) in user_deleted_edges:
    #         user_delete_last_edge(G, new_node_id, u)
    #         user_delete_last_edge(G, v, new_node_id)
    #         print(user_deleted_edges)

    delete_edges(G, u, v, data)
    return new_node_id