import heapq
import delete_clicked_edges
import distance

def reconstruct_path(prev, start, end):
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev.get(node)
    path.reverse()
    return path


def a_star(G, start, end):
    open_heap = []
    heapq.heappush(open_heap, (distance.distance_on_earth(G, start, end), start))

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
                f_score = tentative_g + distance.distance_on_earth(G, neighbor, end)
                heapq.heappush(open_heap, (f_score, neighbor))

    return None


def dijkstra(G, start, end):
    dist = {n: float('inf') for n in G.nodes}
    dist[start] = 0

    prev = {start: None}

    heap = [(0, start)]

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_dist is not dist[current_node]:
            continue

        if current_node == end:
            return reconstruct_path(prev, start, end)

        for _, neighbor, data in G.out_edges(current_node, data=True):
            if str((current_node, neighbor, data)) in map(str, delete_clicked_edges.deleted_edges):
                continue

            weight = data.get('length', 1)
            new_dist = current_dist + weight

            if new_dist < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    return None