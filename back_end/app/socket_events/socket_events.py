from flask import request
from flask_socketio import emit, join_room
from app.services.game import Game

rooms: dict[str, list[str]] = {}  # room id -> [sids]
# sid -> {username, room ID, points, color}
users: dict[str, str, str, str, str] = {}
games: dict[str, Game] = {}  # room id -> current game

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
        print(f"user connected: {sid}")
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

        current_colors = [user["color"]
                          for user in users.values() if user["roomID"] == roomID]
        users[sid]["color"] = [
            color for color in COLORS if color not in current_colors][0]

        emit("player_data", [
             user for user in users.values() if user["roomID"] == users[sid]["roomID"]], room=users[sid]["roomID"])

    @socketio.on("start-game")
    def handle_start_game():
        sid = request.sid
        roomID = users[sid]["roomID"]

        games[roomID] = Game(roomID, list(users.keys()))
        cur_game = games[roomID]

        emit("game_started", True, room=roomID)
        emit("can_execute_move", cur_game.can_execute_move(
            sid), to=sid)
        emit("can_next_move", cur_game.get_current_player()
             == sid, to=sid)

    @socketio.on("button_click")
    def handle_button_click(data):
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.handle_move(sid, data["territory"])

        emit("armies_updated", True, room=users[sid]["roomID"])
        emit("can_execute_move", cur_game.can_execute_move(
            sid), to=sid)
        emit("can_next_move", cur_game.get_current_player()
             == sid, to=sid)

    @socketio.on("execute_move")
    def handle_execute_move():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.execute_move()

        emit("current_phase", cur_game.get_current_phase(),
             room=users[sid]["roomID"])
        emit("armies_updated", True, room=users[sid]["roomID"])
        emit("can_execute_move", cur_game.can_execute_move(
            sid), to=sid)
        emit("can_next_move", cur_game.get_current_player()
             == sid, to=sid)

    @socketio.on("clear_board")
    def handle_clear_board():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.reset_phase()

        emit("armies_updated", True, room=users[sid]["roomID"])
        emit("can_execute_move", cur_game.can_execute_move(
            sid), to=sid)
        emit("can_next_move", cur_game.get_current_player()
             == sid, to=sid)

    @socketio.on("is_current_player")
    def handle_is_current_player():
        sid = request.sid()
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        return cur_player == sid

    @socketio.on("next_move")
    def handle_next_move():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])

        print("next move")
        cur_game.next_move()

        emit("armies_updated", True, room=users[sid]["roomID"])
        emit("can_execute_move", cur_game.can_execute_move(
            sid), to=sid)
        emit("can_next_move", cur_game.get_current_player()
             == sid, to=sid)

        handle_current_phase()
        handle_current_turn()

    @socketio.on("reset_phase")
    def handle_reset_phase():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])
        cur_player = cur_game.get_current_player()

        if sid == cur_player:
            cur_game.reset_phase()

        emit("armies_updated", True, room=users[sid]["roomID"])

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
        cur_player = cur_game.get_current_player()

        emit("current_turn", users[cur_player]
             ["username"], room=users[sid]["roomID"])

    @socketio.on("get_armies")
    def handle_get_armies(data):
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])

        territory = data["territory"]

        get_armies = cur_game.get_string_armies_on_territory(territory)
        get_color = users.get(
            cur_game.get_player_on_territory(territory))["color"]

        is_ter_from = territory in cur_game.get_ter_from()
        is_ter_to = territory in cur_game.get_ter_to()

        return {"num_armies": get_armies, "color": get_color,
                "is_ter_from": is_ter_from, "is_ter_to": is_ter_to}

    @socketio.on("get_terrs")
    def handle_get_terrs():
        sid = request.sid
        cur_game = games.get(users[sid]["roomID"])

        emit("ter_from", cur_game.get_ter_from(), room=users[sid]["roomID"])
        emit("ter_to", cur_game.get_ter_to(), room=users[sid]["roomID"])

    @socketio.on("disconnect")
    def handle_disconnect(reason):
        sid = request.sid
        print(f"user disconnected: {sid}")
        roomID = users.get(sid)["roomID"]
        users.pop(sid, None)

        # update rooms so that the room doesn't contain the name
        if roomID in rooms:
            rooms[roomID] = [i for i in rooms[roomID] if i != sid]
            if not rooms[roomID]:
                del rooms[roomID]

        if roomID in games:
            if not games[roomID]:
                del games[roomID]

        # take the sid out of user rooms
        emit("player_data", [
             user for user in users.values() if user["roomID"] == roomID], room=roomID)
