from datetime import datetime, timezone
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseConfig, BaseModel, Field


class BaseSchema(BaseModel):

    class Config(BaseConfig):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        orm_mode=True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        }


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class IDModelMixin(BaseModel):
    """
    Mixin to add ID field for schemas.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class DateTimeModelMixin(BaseModel):
    """
    Mixin to add create and updated timestamp for schemas.
    """
    created_at: Optional[datetime] = Field(..., alias="created_at")
    last_modified_at: Optional[datetime] = Field(alias="last_modified_at")

