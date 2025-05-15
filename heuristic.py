import math

# Khoảng cách thực tế giữa 2 vị trí dựa trên kinh độ & vĩ độ
def distance_on_earth(G, node1, node2):
    # (lon, lat): (kinh độ, vĩ độ)
    lon1, lat1 = G.nodes[node1]['x'], G.nodes[node1]['y']
    lon2, lat2 = G.nodes[node2]['x'], G.nodes[node2]['y']

    avg_lat_rad = math.radians((lat1 + lat2) / 2)
    x = (lon2 - lon1) * 111 * math.cos(avg_lat_rad)
    y = (lat2 - lat1) * 111
    d = math.sqrt(x**2 + y**2)
    return d # đơn vị: km

# Độ dài đường đi ngắn nhất
def do_dai_duong_di(G, path):
    cal = 0
    for i in range(1, len(path)):
        cal += distance_on_earth(G, path[i - 1], path[i])
    
    return cal

# Khoảng cách euclid giữa 2 điểm
def dist(G, node_A, node_B):
    x1, y1 = G.nodes[node_A]['x'], G.nodes[node_B]['y']
    x2, y2 = G.nodes[node_B]['x'], G.nodes[node_B]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Thuật toán A*
def a_star(G, node_start, node_end):
    open_list = {node_start} # tập các điểm đang xét
    closed_list = set() # tập các điểm đã xét
    g_score = {n: float('inf') for n in G.nodes} # độ dài đường đi từ start -> các đỉnh
    g_score[node_start] = 0
    f_score = {n: float('inf') for n in G.nodes} # độ dài ƯỚC LƯỢNG đường đi từ đỉnh -> đích
    f_score[node_start] = dist(G, node_start, node_end)
    prev = {} # lưu các đỉnh trước đấy của mỗi đỉnh (để backtracking)

    while open_list: # trong khi còn các điểm đang xét
        current = min(open_list, key=lambda n: f_score[n]) # chọn nút có f-score bé nhất

        if current == node_end: # nếu tìm thấy đích rồi thì xử lý -> return
            # reconstruct đường đi
            path = []
            while current in prev:
                path.append(current)
                current = prev[current]
            path.append(node_start)
            return list(reversed(path))
        
        open_list.remove(current)
        closed_list.add(current)

        # Duyệt qua từng cạnh xuất phát từ current
        for _, neighbor, data in G.out_edges(current, data=True): # duyệt qua từng cạnh xuất phát từ current
            if neighbor in closed_list: # nếu đỉnh thăm rồi -> không thăm nữa
                continue

            weight = data.get('length', 1) # lấy độ dài của cạnh
            tentative_g = g_score[current] + weight # tính g-score tạm thời cho đỉnh xét

            if tentative_g < g_score.get(neighbor, float('inf')): # nếu g-score tạm thời < g-score ban đầu -> thay thế
                prev[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + dist(G, neighbor, node_end)
                open_list.add(neighbor)

    return None # trường hợp k tìm thấy đích

# Thuật toán Dijkstra
def dijkstra(G, node_start, node_end):
    node_dist = {n: float('inf') for n in G.nodes} # khởi tạo, độ dài các start -> các nút = vô cùng
    node_dist[node_start] = 0
    prev = {node_start: None} # lưu các đỉnh trước đấy của mỗi đỉnh (để backtracking)
    visited = set()

    while True:
        # chọn đỉnh chưa thăm có khoảng cách nhỏ nhất
        current = min(
            (n for n in G.nodes if n not in visited),
            key=lambda n: node_dist[n], default=None
        )

        # nếu không tìm được đỉnh tiếp theo thì thoát khỏi vòng lặp
        if current is None or node_dist[current] == float('inf') or current == node_end:
            break

        visited.add(current) # thêm current là đã thăm

        for _, neighbor, data in G.out_edges(current, data=True): # duyệt qua từng cạnh xuất phát từ current
            if neighbor in visited: # thăm rồi thì thôi
                continue

            weight = data.get('length', 1) # lấy độ dài của các cạnh
            alt = node_dist[current] + weight # tính độ dài tạm thời start -> đỉnh xét

            if alt < node_dist[neighbor]: # nếu tính tạm thời < độ dài ban đầu -> thay mới
                node_dist[neighbor] = alt
                prev[neighbor] = current

    # Xây dựng lại đường đi = truy vết lại đường đi thông qua mảng prev
    path = []
    node = node_end

    while node is not None:
        path.append(node)
        node = prev.get(node)

    return list(reversed(path))