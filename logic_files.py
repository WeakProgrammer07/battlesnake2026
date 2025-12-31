def get_flood_fill_score(start_node, board_width, board_height, obstacles):
    squares = [start_node]
    visited = []
    visited.append((start_node["x"], start_node["y"]))

    count = 0

    while len(squares) > 0:
        current = squares.pop(0)
        count += 1

        neighbors = [
            {"x": current["x"], "y": current["y"] + 1},
            {"x": current["x"], "y": current["y"] - 1},
            {"x": current["x"] - 1, "y": current["y"]},
            {"x": current["x"] + 1, "y": current["y"]}
        ]

        for n in neighbors:
            if (0 <= n["x"] < board_width and 
                0 <= n["y"] < board_height and 
                (n["x"], n["y"]) not in obstacles and 
                (n["x"], n["y"]) not in visited):
                
                visited.append((n["x"], n["y"]))
                squares.append(n)

    return count

def a_star(start, goal, grid_width, grid_height, obstacles):
    start_pos = (start["x"], start["y"])
    goal_pos = (goal["x"], goal["y"])
    
    open_list = [(0, start_pos)]
    
    came_from = {}
    g_score = {start_pos: 0}

    obstacle_set = {(o["x"], o["y"]) for o in obstacles}

    while open_list:
        current_idx = 0
        for i in range(len(open_list)):
            if open_list[i][0] < open_list[current_idx][0]:
                current_idx = i
        
        # Remove and get the current node
        current_f, current = open_list.pop(current_idx)

        # at goal?
        if current == goal_pos:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        # neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if not (0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height):
                continue
            if neighbor in obstacle_set:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                
                h_score = abs(neighbor[0] - goal_pos[0]) + abs(neighbor[1] - goal_pos[1])
                f_score = tentative_g_score + h_score
                
                open_list.append((f_score, neighbor))
                
    return [] # No path found