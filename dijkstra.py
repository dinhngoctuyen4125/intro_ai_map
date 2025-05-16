import heapq
import node_handling

def reconstruct_path(prev, start, end):
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev.get(node)
    path.reverse()
    return path

def heuristic(G, start, end):
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
            if str((current_node, neighbor, data)) in map(str, node_handling.user_deleted_edges):
                continue

            weight = data.get('length', 1)
            new_dist = current_dist + weight

            if new_dist < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    return None
