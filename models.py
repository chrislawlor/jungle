import os
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


USERS_TABLE = os.environ.get("USERS_TABLE", "users-dev")
PLANTS_TABLE = os.environ.get("PLANTS_TABLE", "plants-dev")
USER_PLANTS_TABLE = os.environ.get("USER_PLANTS_TABLE", "user-plant-dev")


class Auth0Signup(BaseModel):
    """
    {
        "sub": "google-oauth2|109695023672787580804",
        "given_name": "Chris",
        "family_name": "Lawlor",
        "nickname": "lawlor.chris",
        "name": "Chris Lawlor",
        "picture": "https://lh3.googleusercontent.com/a-/AOh14GhdCN6Ro1yvZUgd_ZfRL-YwxyclXM3jgN2XSBpq0Q=s96-c",
        "locale": "en",
        "updated_at": "2021-06-05T14:10:29.656Z"
    }
    """

    # From Google
    sub: str
    given_name: str
    family_name: str
    nickname: str
    name: str
    picture: str  # URL
    locale: str  # ISO 3166-1 alpha-2  https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    updated_at: datetime


# DynamoDB Models
# These need to be added manually to serverless.yml


class User(BaseModel):
    __tablename__ = USERS_TABLE
    uid: Optional[str]
    name: str


class Plant(BaseModel):
    __tablename__ = PLANTS_TABLE
    uid: Optional[str]
    common_name: str
    scientific_name: str
    slug: str
    image: Optional[str]  # URL
    watering_interval_days: Optional[int]
    fertilize_interval_days: Optional[int]
    added_by: str  # user ID


class PlantCareEvent(BaseModel):
    # nested in UserPlant
    timestamp: datetime
    notes: str = ""


class UserPlant(BaseModel):
    __tablename__ = USER_PLANTS_TABLE
    uid: Optional[str]
    user_id: str
    plant_id: str
    nickname: str = ""
    watering_interval_days: Optional[int]
    fertilize_interval_days: Optional[int]
    watering_events: List[PlantCareEvent] = []
    fertilizing_events: List[PlantCareEvent] = []
    notes: List[PlantCareEvent] = []
    images: List[str] = []
