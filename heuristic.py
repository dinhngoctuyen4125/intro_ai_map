import heapq
import math

def heuristic(G, node, node_end):
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
    f_score = {node: float('inf') for node in G.nodes}  # Chi phí tổng (g + heuristic)
    f_score[node_start] = heuristic(G, node_start, node_end)  # Khoảng cách từ start đến end

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
            f_score[neighbor] = g_score[neighbor] + heuristic(G, neighbor, node_end)

    return None  # Nếu không tìm thấy đường đi
