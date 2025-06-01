from flask import request
from flask_socketio import emit, join_room

rooms = {}  # room id -> sid
users = {}  # sid -> {username, room ID, points}


def register_socket_events(socketio):
    @socketio.on("connect")
    def handle_connect():
        # print(f"user connected: {request.sid}")
        users[request.sid] = {"username": None, "roomID": None, "points": 0}

        emit("server_response", {"message": f"user connected: {request.sid}"})

    @socketio.on("button_click")
    def handle_button_click():
        sid = request.sid

        print(f"button clicked by {sid}")
        users[sid]["points"] += 1

        emit("player_data", [
             user for user in users.values() if user["roomID"] == users[sid]["roomID"]], room=users[sid]["roomID"])

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

        emit("room-users", [users[key]
             for key in rooms[roomID] if key in users], room=roomID)
        emit("player_data", [
             user for user in users.values() if user["roomID"] == users[sid]["roomID"]], room=users[sid]["roomID"])

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
