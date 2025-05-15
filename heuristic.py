import heapq
import math

def dist(G, node, node_end):
    x1, y1 = G.nodes[node]['x'], G.nodes[node]['y']
    x2, y2 = G.nodes[node_end]['x'], G.nodes[node_end]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Thuật toán A*
def a_star(G, node_start, node_end):
    # Khởi tạo các cấu trúc dữ liệu
    open_list = set([node_start])  # Các node sẽ được kiểm tra
    closed_list = set()  # Các node đã được kiểm tra
    g_score = {node: float('inf') for node in G.nodes}  # Chi phí từ node_start đến các node khác
    g_score[node_start] = 0  # Chi phí từ start đến start là 0
    f_score = {node: float('inf') for node in G.nodes}  # Chi phí tổng (g + dist)
    f_score[node_start] = dist(G, node_start, node_end)  # Khoảng cách từ start đến end

    came_from = {}  # Dùng để truy vết đường đi

    while open_list:
        # Chọn node có f_score thấp nhất từ open_list
        current_node = min(open_list, key=lambda node: f_score[node])
        
        # Nếu đã đến node_end, ta đã tìm được đường đi ngắn nhất
        if current_node == node_end:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(node_start)
            path.reverse()  # Đảo ngược đường đi từ node_start đến node_end
            return path
        
        open_list.remove(current_node)
        closed_list.add(current_node)

        # Xử lý các node kề của current_node
        for neighbor in G.neighbors(current_node):
            if neighbor in closed_list:
                continue  # Nếu đã kiểm tra node này thì bỏ qua
            
            tentative_g_score = g_score[current_node] + G[current_node][neighbor].get('length', 1)

            if neighbor not in open_list:
                open_list.add(neighbor)
            elif tentative_g_score >= g_score[neighbor]:
                continue  # Nếu đường đi mới không tốt hơn thì bỏ qua

            # Cập nhật g_score và f_score
            came_from[neighbor] = current_node
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + dist(G, neighbor, node_end)

    return None  # Nếu không tìm thấy đường đi

def dijkstra(G, node_start, node_end):
    # Khởi tạo các cấu trúc dữ liệu
    unvisited_nodes = list(G.nodes)
    shortest_path = {}  # Để lưu đường đi ngắn nhất
    shortest_path[node_start] = None
    node_distances = {node: float('inf') for node in G.nodes}
    node_distances[node_start] = 0

    while unvisited_nodes:
        # Chọn node chưa thăm có khoảng cách ngắn nhất
        current_node = None
        for node in unvisited_nodes:
            if current_node is None:
                current_node = node
            elif node_distances[node] < node_distances[current_node]:
                current_node = node

        # Nếu khoảng cách đến current_node là vô cùng (không có đường đi đến node này), dừng thuật toán
        if node_distances[current_node] == float('inf'):
            break

        # Lấy các neighbors của current_node
        neighbors = G.neighbors(current_node)

        for neighbor in neighbors:
            # Tính khoảng cách từ current_node đến neighbor
            edge_weight = G[current_node][neighbor].get('length', 1)  # Chiều dài của cạnh
            alternative_route = node_distances[current_node] + edge_weight

            # Nếu tìm được đường đi ngắn hơn, cập nhật giá trị
            if alternative_route < node_distances[neighbor]:
                node_distances[neighbor] = alternative_route
                shortest_path[neighbor] = current_node

        # Đánh dấu current_node là đã thăm xong
        unvisited_nodes.remove(current_node)

    # Tạo đường đi từ node_end đến node_start (ngược lại)
    path = []
    current_node = node_end
    while current_node != node_start:
        path.append(current_node)
        current_node = shortest_path[current_node]
    path.append(node_start)
    path.reverse()  # Đảo ngược lại để có đường đi từ node_start đến node_end

    return path