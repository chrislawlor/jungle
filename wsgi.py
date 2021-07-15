from app import create_app
from persistence import Repository
from models import User, Plant, UserPlant


app = create_app(
    user_repo=Repository.for_model(User),
    plant_repo=Repository.for_model(Plant),
    userplant_repo=Repository.for_model(UserPlant),
)
