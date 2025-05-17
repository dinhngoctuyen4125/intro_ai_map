import math
import heapq
import delete_clicked_edges

def reconstruct_path(prev, start, end):
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev.get(node)
    path.reverse()
    return path

def dist(G, node_A, node_B):
    x1, y1 = G.nodes[node_A]['x'], G.nodes[node_A]['y']
    x2, y2 = G.nodes[node_B]['x'], G.nodes[node_B]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def heuristic(G, start, end):
    open_heap = []
    heapq.heappush(open_heap, (dist(G, start, end), start))

    closed_set = set()
    g_score = {n: float('inf') for n in G.nodes}
    g_score[start] = 0
    prev = {start: None}

    while open_heap:
        current_f, current_node = heapq.heappop(open_heap)

        if current_node in closed_set:
            continue
        closed_set.add(current_node)

        if current_node == end:
            return reconstruct_path(prev, start, end)

        for _, neighbor, data in G.out_edges(current_node, data=True):
            if str((current_node, neighbor, data)) in map(str, delete_clicked_edges.deleted_edges):
                continue
            if neighbor in closed_set:
                continue

            weight = data.get('length', 1)
            tentative_g = g_score[current_node] + weight

            if tentative_g < g_score.get(neighbor, float('inf')):
                prev[neighbor] = current_node
                g_score[neighbor] = tentative_g
                f_score = tentative_g + dist(G, neighbor, end)
                heapq.heappush(open_heap, (f_score, neighbor))

    return None
