import node_handling

# Thuật toán Dijkstra
def heuristic(G, node_start, node_end):
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
            if str((current, neighbor, data)) in map(str, node_handling.user_deleted_edges):
                print("XXXXX")
                continue
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