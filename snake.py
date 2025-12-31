from flask import Flask, request
from logic_files import get_flood_fill_score, a_star

app = Flask(__name__)

@app.route("/", methods=["GET"])
def handle_info():
    print("INFO: Received a health check request")
    return {
        "apiversion": "1",
        "author": "liamwallace",
        "color": "#e80202",
        "head": "default",
        "tail": "default"
    }

@app.post("/start")
def handle_start():
    return "ok"

@app.post("/move")
def handle_move():
    #gets the data given by board
    data = request.get_json()
    possible_directions = {
        "left": 100,
        "right": 100,
        "up": 100,
        "down": 100
    }

    my_head = data["you"]["body"][0]
    board_width = data["board"]["width"]
    board_height = data["board"]["height"]

    #border collsion check
    if (my_head["x"] - 1) < 0:
        possible_directions["left"] = -1
    if (my_head["x"] + 1) >= board_width:
        possible_directions["right"] = -1
    if (my_head["y"] - 1) < 0:
        possible_directions["down"] = -1
    if (my_head["y"] + 1) >= board_height:
        possible_directions["up"] = -1

    #create set of all obsticales
    all_obstacles = set()
    for snake in data["board"]["snakes"]:
        for segment in snake["body"][:-1]:
            all_obstacles.add((segment["x"], segment["y"]))

    #collision check
    if (my_head["x"] - 1, my_head["y"]) in all_obstacles:
        possible_directions["left"] = -1
    if (my_head["x"] + 1, my_head["y"]) in all_obstacles:
        possible_directions["right"] = -1
    if (my_head["x"], my_head["y"] - 1) in all_obstacles:
        possible_directions["down"] = -1
    if (my_head["x"], my_head["y"] + 1) in all_obstacles:
        possible_directions["up"] = -1

    #flood fill all sections
    flood_mult = 0.5
    if possible_directions["left"] != -1:
        left_node = {"x": my_head["x"] - 1, "y": my_head["y"]}
        left_flood = get_flood_fill_score(left_node, board_width, board_height, all_obstacles)
        possible_directions["left"] += left_flood * flood_mult

    if possible_directions["right"] != -1:
        right_node = {"x": my_head["x"] + 1, "y": my_head["y"]}
        right_flood = get_flood_fill_score(right_node, board_width, board_height, all_obstacles)
        possible_directions["right"] += right_flood * flood_mult

    if possible_directions["down"] != -1:
        down_node = {"x": my_head["x"], "y": my_head["y"] - 1}
        down_flood = get_flood_fill_score(down_node, board_width, board_height, all_obstacles)
        possible_directions["down"] += down_flood * flood_mult

    if possible_directions["up"] != -1:
        up_node = {"x": my_head["x"], "y": my_head["y"] + 1}
        up_flood = get_flood_fill_score(up_node, board_width, board_height, all_obstacles)
        possible_directions["up"] += up_flood * flood_mult

    #incentive to follow tail
    tail_incentive = 50
    my_tail = data["you"]["body"][-1]
    if possible_directions["left"] != -1:
        if my_head["x"] - 1 == my_tail["x"] and my_head["y"] == my_tail["y"]:
            possible_directions["left"] += tail_incentive
    if possible_directions["right"] != -1:
        if my_head["x"] + 1 == my_tail["x"] and my_head["y"] == my_tail["y"]:
            possible_directions["right"] += tail_incentive
    if possible_directions["down"] != -1:    
        if my_head["y"] - 1 == my_tail["y"] and my_head["x"] == my_tail["x"]:
            possible_directions["down"] += tail_incentive
    if possible_directions["up"] != -1:    
        if my_head["y"] + 1 == my_tail["y"] and my_head["x"] == my_tail["x"]:
            possible_directions["up"] += tail_incentive

    my_health = data["you"]["health"]
    if my_health < 10:
        low_health_mod = 50
    elif my_health < 25:
        low_health_mod = 10
    elif my_health < 50:
        low_health_mod = 3
    elif my_health < 75:
        low_health_mod = 2
    else:
        low_health_mod = 1
    
    #more incentive to go for food in the beginning
    turn = data["turn"]
    if turn < 40:
        turn_mult = 20
    elif turn < 100:
        turn_mult = 5
    else:
        turn_mult = 1

    # food checker using A*
    food_list = data["board"]["food"]
    best_path = []
    shortest_path_len = 9999

    for food in food_list:
        path = a_star(my_head, food, board_width, board_height, all_obstacles)
        
        if path and len(path) < shortest_path_len:
            shortest_path_len = len(path)
            best_path = path

    if best_path:
        first_step = best_path[0] # This is (x, y)
        food_reward = 1 * low_health_mod * turn_mult
 
        if first_step[0] < my_head["x"]:
            possible_directions["left"] += food_reward
        elif first_step[0] > my_head["x"]:
            possible_directions["right"] += food_reward
        elif first_step[1] < my_head["y"]:
            possible_directions["down"] += food_reward
        elif first_step[1] > my_head["y"]:
            possible_directions["up"] += food_reward

    #list of possible risky moves
    my_id = data["you"]["id"]
    my_length = data["you"]["length"]
    for snake in data["board"]["snakes"]:
        if snake["id"] == my_id:
            continue
            
        opp_head = snake["head"]
        opp_length = snake["length"]
        
        opp_moves = [
            {"x": opp_head["x"], "y": opp_head["y"] + 1},
            {"x": opp_head["x"], "y": opp_head["y"] - 1},
            {"x": opp_head["x"] - 1, "y": opp_head["y"]},
            {"x": opp_head["x"] + 1, "y": opp_head["y"]}
        ]
        
        for move in opp_moves:
            if possible_directions["left"] != -1:
                if (my_head["x"] - 1) == move["x"] and my_head["y"] == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["left"] -= 100
                    else:
                        possible_directions["left"] += 1000

            if possible_directions["right"] != -1:
                if (my_head["x"] + 1) == move["x"] and my_head["y"] == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["right"] -= 100
                    else:
                        possible_directions["right"] += 1000
            
            if possible_directions["down"] != -1:
                if my_head["x"] == move["x"] and (my_head["y"] - 1) == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["down"] -= 100
                    else:
                        possible_directions["down"] += 1000

            if possible_directions["up"] != -1:
                if my_head["x"] == move["x"] and (my_head["y"] + 1) == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["up"] -= 100
                    else:
                        possible_directions["up"] += 1000

    print(data["turn"])
    best_move = max(possible_directions, key=possible_directions.get)
    print(possible_directions)
    
    return {"move": best_move}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)