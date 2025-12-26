from flask import Flask, request

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
        "left": 0,
        "right": 0,
        "up": 0,
        "down": 0
    }
    my_head = data["you"]["body"][0]
    print(my_head)

    #left movement checks

    #right movement checks

    #up movement checks

    #down movement checks


    direction = "left"
    print(data["turn"])
    
    return {"move": direction}

if __name__ == "__main__":
    app.run(port=8080)