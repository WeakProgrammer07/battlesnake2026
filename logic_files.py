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

def find_closest_food(my_head, food_list):
    closest_food = food_list[0]
    min_distance = 9999 

    for food in food_list:
        dist = abs(my_head["x"] - food["x"]) + abs(my_head["y"] - food["y"])
        
        if dist < min_distance:
            min_distance = dist
            closest_food = food

    return closest_food