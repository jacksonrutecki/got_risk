from app.socket_events.socket_events import register_socket_events
from app.routes.map_routes import map_bp
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO


def create_app():
    app = Flask(__name__)
    CORS(app)

    socketio = SocketIO(app, cors_allowed_origins="*")

    app.register_blueprint(map_bp, url_prefix="/app")

    register_socket_events(socketio)

    return app, socketio
