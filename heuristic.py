import heapq
import math

def distance_on_earth(G, node1, node2): # khoảng cách thực tế giữa 2 vị trí dựa trên kinh độ vĩ độ
    # (lon, lat): (kinh độ, vĩ độ)
    lon1, lat1 = G.nodes[node1]['x'], G.nodes[node1]['y']
    lon2, lat2 = G.nodes[node2]['x'], G.nodes[node2]['y']

    avg_lat_rad = math.radians((lat1 + lat2) / 2)
    x = (lon2 - lon1) * 111 * math.cos(avg_lat_rad)
    y = (lat2 - lat1) * 111
    d = math.sqrt(x**2 + y**2)
    return d  # km

def do_dai_duong_di(G, path):
    cal = 0
    for i in range(1, len(path)):
        cal += distance_on_earth(G, path[i - 1], path[i])
    
    return cal

def dist(G, node, node_end):
    x1, y1 = G.nodes[node]['x'], G.nodes[node]['y']
    x2, y2 = G.nodes[node_end]['x'], G.nodes[node_end]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Thuật toán A*
def a_star(G, node_start, node_end):
    open_list = {node_start}
    closed_list = set()
    g_score = {n: float('inf') for n in G.nodes}
    g_score[node_start] = 0
    f_score = {n: float('inf') for n in G.nodes}
    f_score[node_start] = dist(G, node_start, node_end)
    came_from = {}

    while open_list:
        current = min(open_list, key=lambda n: f_score[n])
        if current == node_end:
            # Reconstruct đường đi
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(node_start)
            return list(reversed(path))
        open_list.remove(current)
        closed_list.add(current)

        # Duyệt qua từng cạnh xuất phát từ current
        for _, neighbor, data in G.out_edges(current, data=True):
            if neighbor in closed_list:
                continue
            weight = data.get('length', 1)
            tentative_g = g_score[current] + weight
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + dist(G, neighbor, node_end)
                open_list.add(neighbor)
    return None

# Thuật toán Dijkstra
def dijkstra(G, node_start, node_end):
    node_dist = {n: float('inf') for n in G.nodes}
    node_dist[node_start] = 0
    prev = {node_start: None}
    visited = set()

    while True:
        # Chọn đỉnh chưa thăm có khoảng cách nhỏ nhất
        current = min(
            (n for n in G.nodes if n not in visited),
            key=lambda n: node_dist[n], default=None
        )
        if current is None or node_dist[current] == float('inf') or current == node_end:
            break
        visited.add(current)

        for _, neighbor, data in G.out_edges(current, data=True):
            if neighbor in visited:
                continue
            weight = data.get('length', 1)
            alt = node_dist[current] + weight
            if alt < node_dist[neighbor]:
                node_dist[neighbor] = alt
                prev[neighbor] = current

    # Xây dựng lại đường đi
    path = []
    node = node_end
    while node is not None:
        path.append(node)
        node = prev.get(node)
    return list(reversed(path))