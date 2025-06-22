from flask import jsonify, request, Blueprint
from app.services.map_logic import get_files_in_dir

map_bp = Blueprint("app", __name__)


@map_bp.route("/list-files", methods=["GET"])
def list_files():
    directory = request.args.get("directory")
    file_data = get_files_in_dir(directory.replace("back_end/", ""))

    return jsonify(file_data)
