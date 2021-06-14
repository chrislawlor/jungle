import os
from hashlib import md5
from os import urandom

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

dynamodb_client = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb")


if os.environ.get("IS_OFFLINE"):
    dynamodb_client = boto3.client(
        "dynamodb", region_name="localhost", endpoint_url="http://localhost:8000"
    )
    dynamodb_resource = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")


class DoesNotExist(ValueError):
    pass


class Repository:
    def __init__(self, model_class, table):
        assert issubclass(model_class, BaseModel)
        self.model_class = model_class
        self.table = table

    @classmethod
    def for_model(cls, model_class):
        table = dynamodb_resource.Table(model_class.__tablename__)
        return cls(model_class, table)

    def get(self, uid: str):
        resp = self.table.get_item(Key={"uid": uid})
        if "Item" not in resp:
            raise DoesNotExist(
                f"{self.model_class.schema()['title']} object '{uid}' does not exist"
            )
        return self.model_class(**resp["Item"])

    def save(self, instance):
        if not instance.uid:
            self.put(instance)
        else:
            self.update(instance)

    def put(self, instance) -> None:
        if instance.uid:
            raise ValueError("Use update for items that already have an ID")
        uid = self.create_id()
        # Don't set instance.uid until save is successful
        item_dict = instance.dict()
        item_dict["uid"] = uid
        self.table.put_item(Item=item_dict)
        instance.uid = uid

    def update(self, instance) -> None:
        item_dict = instance.dict()
        uid = item_dict.pop("uid")
        self.table.update_item(Key={"uid": uid}, AttributeUpdates=item_dict)

    def delete(self, uid: str):
        self.table.delete_item(Key={"uid": uid})

    def filter(self, key, value):
        resp = self.table.query(KeyConditionExpression=Key(key).eq(value))
        if "Items" not in resp:
            return []
        return [self.model_class(**data) for data in resp["Items"]]

    def list(self):
        resp = self.table.scan()
        if "Items" not in resp:
            return []
        return [self.model_class(**data) for data in resp["Items"]]

    @staticmethod
    def create_id() -> str:
        return md5(urandom(20)).hexdigest()
