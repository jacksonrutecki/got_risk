from flask import request
from flask_socketio import emit, join_room
from app.services.game import Game

rooms = {}  # room id -> sid
users = {}  # sid -> {username, room ID, points, color}
games = {}  # room id -> current game

COLORS = ["#E74C3C",
          "#3498DB",
          "#2ECC71",
          "#E67E22",
          "#9B59B6",
          "#F1C40F",
          "#1ABC9C",
          "#E91E63"]


def register_socket_events(socketio):
    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        print(f"user disconnected: {sid}")
        users[sid] = {"username": None,
                      "roomID": None, "points": 0, "color": None}

    @socketio.on("join-room")
    def handle_join_room(data):
        roomID = data["roomID"]
        username = data["username"]
        sid = request.sid

        join_room(roomID)

        # create new room if its not there already
        if roomID not in rooms:
            rooms[roomID] = []
        # if the player is not in the room, add them
        elif not any(i == sid for i in rooms[roomID]):
            rooms[roomID].append(sid)

        # update username and room id of the user accordingly
        users[sid]["roomID"] = roomID
        users[sid]["username"] = username
        users[sid]["color"] = COLORS[len(rooms[roomID]) - 2]

        print(users)
        emit("player_data", [
             user for user in users.values() if user["roomID"] == users[sid]["roomID"]], room=users[sid]["roomID"])

    @socketio.on("start-game")
    def handle_start_game():
        sid = request.sid
        roomID = users[sid]["roomID"]

        games[roomID] = Game(roomID, list(users.keys()))

    @socketio.on("button_click")
    def handle_button_click(data):
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.handle_move(sid, data["territory"])

        emit("armies_updated", True)
        print(cur_game.get_ter_to())

    @socketio.on("execute_move")
    def handle_execute_move():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.execute_move()

        emit("armies_updated", True)

    @socketio.on("reset_phase")
    def handle_reset_phase():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.reset_phase()

        emit("armies_updated", True)

    @socketio.on("get_current_phase")
    def handle_current_phase():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])

        emit("current_phase", cur_game.get_current_phase(),
             room=users[sid]["roomID"])

    @socketio.on("get_current_turn")
    def handle_current_turn():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        current_turn_sid = cur_game.get_current_player()

        emit("current_turn", users[current_turn_sid]["username"],
             room=users[sid]["roomID"])

    @socketio.on("get_armies")
    def handle_get_armies(data):
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])

        territory = data["territory"]

        get_armies = cur_game.get_num_armies_on_territory(territory)
        get_color = users.get(
            cur_game.__get_player_on_territory__(territory))["color"]

        is_ter_from = territory in cur_game.get_ter_from()
        is_ter_to = territory in cur_game.get_ter_to()

        emit("num_armies", {"num_armies": get_armies, "color": get_color,
             "is_ter_from": is_ter_from, "is_ter_to": is_ter_to})

    @socketio.on("get_terrs")
    def handle_get_terrs(data):
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])

        emit("ter_from", cur_game.get_ter_from())
        emit("ter_to", cur_game.get_ter_to())

    @socketio.on("next_move")
    def handle_next_move():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_game.next_move()

    @socketio.on("disconnect")
    def handle_disconnect(reason):
        sid = request.sid
        print(f"user disconnected: {sid}")

        # update rooms so that the room doesn't contain the name
        roomID = users.get(sid)["roomID"]
        if roomID in rooms:
            rooms[roomID] = [i for i in rooms[roomID] if i != sid]
            emit("room-users", [users[key]
                 for key in rooms[roomID] if key in users], room=roomID)
            if not rooms[roomID]:
                del rooms[roomID]

        # take the sid out of user rooms
        emit("player_data", [
             user for user in users.values() if user["roomID"] == users[sid]["roomID"]], room=users[sid]["roomID"])
        users.pop(sid, None)
