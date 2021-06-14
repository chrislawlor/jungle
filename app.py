from flask import Flask, jsonify, make_response, request
from persistence import Repository
from models import User, Plant, UserPlant
from pydantic import ValidationError

from middleware import ApiErrorResponseMiddleware

app = Flask(__name__)

app.wsgi_app = ApiErrorResponseMiddleware(app.wsgi_app)


@app.route("/users", methods=["POST"])
def create_user():
    user = User(**request.json)
    repo = Repository.for_model(User)
    repo.save(user)
    return jsonify(user.dict())


@app.route("/users/<string:user_id>")
def get_user(user_id):
    repo = Repository.for_model(User)
    user = repo.get(uid=user_id)
    if not user:
        return jsonify({"error": 'Could not find user with provided "userId"'}), 404

    return jsonify(user.dict())


@app.route("/plants", methods=["GET", "POST"])
def list_create_plants():
    repo = Repository.for_model(Plant)
    if request.method == "GET":
        return jsonify([p.dict() for p in repo.list()])
    plant = Plant(**request.json)
    repo.save(plant)
    return jsonify(plant.dict())


@app.route("/users/<string:user_id>/plants", methods=["GET", "POST"])
def list_create_user_plants(user_id):
    userplant_repo = Repository.for_model(UserPlant)
    if request.method == "GET":
        plants = userplant_repo.filter("user_id", user_id)
        return jsonify([p.dict() for p in plants])
    data = request.json
    data["user_id"] = user_id
    plant_repo = Repository.for_model(Plant)
    userplant = UserPlant(**data)

    # Check plant ID is valid
    plant_repo.get(uid=userplant.plant_id)

    userplant_repo.save(userplant)
    return jsonify(userplant.dict())


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error="Not found!"), 404)
