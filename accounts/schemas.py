from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from pydantic.fields import Field
from core.mixins import BaseSchema, DateTimeModelMixin, IDModelMixin


class UserTypeEnum(str, Enum):
    admin = "admin"
    user = "user"


class UserBase(BaseSchema):
    """Base Schema for all User resources.

    Args:
        BaseSchema (Type[BaseModel]): Custom pydantic BaseModel for schema.
    """
    user_id: Optional[str]
    user_role: Optional[UserTypeEnum]
    email: Optional[EmailStr]
    is_active: Optional[bool]


class UserCreate(UserBase):
    """Create schema for users.

    Args:
        UserBase (Model): Base model schema for User resources.
    """
    user_id: str = Field(..., alias="user_id")
    user_role: UserTypeEnum = UserTypeEnum.user
    email: EmailStr = None
    is_active: bool = True
    created_at: datetime = datetime.now()


class UserUpdate(UserBase):
    """Update schema for users.

    Args:
        UserBase (Model): Base model schema for User resources.
    """
    updated_at: datetime = datetime.now()


class UserInDB(DateTimeModelMixin, UserBase, IDModelMixin):
    """User schema for DB structure.

    Args:
        IDModelMixin (Type[BaseModel]): ID mixin for db id field.
        DateTimeModelMixin (Type[BaseModel]): Datetime model mixin for created_at and updated_at field.
        UserBase (Model): Base model schema for User resources.
    """
    pass


class UserOut(UserInDB):
    pass
