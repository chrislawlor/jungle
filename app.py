import json
from typing import Dict

import falcon
from pydantic import ValidationError

from models import Plant, User, UserPlant
from persistence import DoesNotExist, Repository


class PlantCollection:
    def __init__(self, repo: Repository):
        self.repo = repo

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        resp.text = json.dumps({"plants": [p.dict() for p in self.repo.list()]})

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        data = json.load(req.bounded_stream)
        plant = Plant(**data)
        self.repo.save(plant)
        resp.text = json.dumps({"plant": plant.dict()})


class PlantResource:
    def __init__(self, repo: Repository):
        self.repo = repo

    def on_get(self, _, resp: falcon.Response, plant_id: str):
        repo = Repository.for_model(Plant)
        try:
            plant = repo.get(uid=plant_id)
            resp.text = json.dumps(plant.dict())
        except DoesNotExist as e:
            raise falcon.HTTPNotFound() from e


class UserResource:
    def __init__(self, repo: Repository):
        self.repo = repo

    def on_get(self, _, resp: falcon.Response, user_id: str):
        user = self.repo.get(uid=user_id)
        resp.text = json.dumps({"user": user.dict()})


class UserCollection:
    def __init__(self, repo: Repository):
        self.repo = repo

    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)
        user = User(**data)
        self.repo.save(user)
        resp.text = json.dumps({"user": user.dict()})


class UserPlantCollection:
    def __init__(
        self, plant_repo: Repository, user_repo: Repository, userplant_repo: Repository
    ):
        self.plant_repo = plant_repo
        self.user_repo = user_repo
        self.userplant_repo = userplant_repo

    def on_get(self, req: falcon.Request, resp: falcon.Response, user_id: str):
        print(f"{user_id=}")
        userplants = self.userplant_repo.filter("user_id", user_id)
        resp.text = json.dumps({"userplants": [p.dict() for p in userplants]})

    def on_post(self, req: falcon.Request, resp: falcon.Response, user_id: str):
        # check user_id is valid
        user = self.user_repo.get(uid=user_id)

        data = json.load(req.bounded_stream)

        data["user_id"] = user_id
        userplant = UserPlant(**data)

        # check plant ID is valid
        self.plant_repo.get(uid=userplant.plant_id)

        self.userplant_repo.save(userplant)
        resp.text = json.dumps({"userplant": userplant.dict()})


def handle_validation_error(
    req: falcon.Request, resp: falcon.Response, ex: ValidationError, params: Dict[str, str]
):
    resp.status = falcon.HTTP_400
    resp.text = ex.json()


def create_app(
    user_repo: Repository, plant_repo: Repository, userplant_repo: Repository
):
    app = falcon.App()
    app.add_route("/plants", PlantCollection(plant_repo)),
    app.add_route("/plants/{plant_id}", PlantResource(plant_repo))
    app.add_route("/users", UserCollection(user_repo))
    app.add_route("/users/{user_id}", UserResource(user_repo))
    app.add_route(
        "/users/{user_id}/plants",
        UserPlantCollection(
            plant_repo=plant_repo, user_repo=user_repo, userplant_repo=userplant_repo
        ),
    )

    app.add_error_handler(ValidationError, handle_validation_error)
    return app
