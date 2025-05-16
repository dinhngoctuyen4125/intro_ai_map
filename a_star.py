import math
import node_handling

# Khoảng cách euclid giữa 2 điểm
def dist(G, node_A, node_B):
    x1, y1 = G.nodes[node_A]['x'], G.nodes[node_B]['y']
    x2, y2 = G.nodes[node_B]['x'], G.nodes[node_B]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Thuật toán A*
def heuristic(G, node_start, node_end):
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
            print ((current, neighbor, data))
            if str((current, neighbor, data)) in map(str, node_handling.user_deleted_edges):
                print("XXXXX")
                continue
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