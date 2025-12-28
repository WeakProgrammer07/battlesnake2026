from flask import Flask, request
from logic_files import get_flood_fill_score, find_closest_food

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
    my_tail = data["you"]["body"][-1]
    if possible_directions["left"] != -1:
        if my_head["x"] - 1 == my_tail["x"] and my_head["y"] == my_tail["y"]:
            possible_directions["left"] += 25
    if possible_directions["right"] != -1:
        if my_head["x"] + 1 == my_tail["x"] and my_head["y"] == my_tail["y"]:
            possible_directions["right"] += 25
    if possible_directions["down"] != -1:    
        if my_head["y"] - 1 == my_tail["y"] and my_head["x"] == my_tail["x"]:
            possible_directions["down"] += 25
    if possible_directions["up"] != -1:    
        if my_head["y"] + 1 == my_tail["y"] and my_head["x"] == my_tail["x"]:
            possible_directions["up"] += 25

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
        turn_mult = 10
    else:
        turn_mult = 2

    #food checker
    closest_food = find_closest_food(my_head, data["board"]["food"])
    if possible_directions["left"] != -1:
        if closest_food["x"] < my_head["x"]:
            possible_directions["left"] += 1 * low_health_mod * turn_mult
    if possible_directions["right"] != -1:
        if closest_food["x"] > my_head["x"]:
            possible_directions["right"] += 1 * low_health_mod * turn_mult
    if possible_directions["down"] != -1:
        if closest_food["y"] < my_head["y"]:
            possible_directions["down"] += 1 * low_health_mod * turn_mult
    if possible_directions["up"] != -1:
        if closest_food["y"] > my_head["y"]:
            possible_directions["up"] += 1 * low_health_mod * turn_mult

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
                        possible_directions["left"] += 100

            if possible_directions["right"] != -1:
                if (my_head["x"] + 1) == move["x"] and my_head["y"] == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["right"] -= 100
                    else:
                        possible_directions["right"] += 100
            
            if possible_directions["down"] != -1:
                if my_head["x"] == move["x"] and (my_head["y"] - 1) == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["down"] -= 100
                    else:
                        possible_directions["down"] += 100

            if possible_directions["up"] != -1:
                if my_head["x"] == move["x"] and (my_head["y"] + 1) == move["y"]:
                    if opp_length >= my_length:
                        possible_directions["up"] -= 100
                    else:
                        possible_directions["up"] += 100

    print(data["turn"])
    best_move = max(possible_directions, key=possible_directions.get)
    print(possible_directions)
    
    return {"move": best_move}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)