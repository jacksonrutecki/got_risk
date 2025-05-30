from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


@app.route("/list-files", methods=["GET"])
def list_files():
    directory = request.args.get("directory")
    file_data = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                content = f.read().strip()
                file_data.append({"id": filename, "d": content})

    return jsonify(file_data)


if __name__ == "__main__":
    app.run()
