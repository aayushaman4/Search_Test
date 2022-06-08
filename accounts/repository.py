from typing import Type

from src.accounts.schemas import UserCreate, UserOut, UserTypeEnum, UserUpdate
from src.core.config import log
from src.core.constants import Collections
from src.db.repository import BaseRepository


class UserRepository(BaseRepository):

    @property
    def _db_collection(self):
        return Collections.user_collection

    @property
    def _schema_out(self) -> Type[UserOut]:
        return UserOut

    @property
    def _schema_create(self) -> Type[UserCreate]:
        return UserCreate

    @property
    def _schema_update(self) -> Type[UserUpdate]:
        return UserUpdate

    async def get(self, cognito_user_id: str):
        """Get user for reviews and ratings service.

        Args:
            cognito_user_id (str): User id provided by aws cognito fetched from bearer token

        Returns:
            user (object): User object from database
        """
        if (user := await self._collection.find_one({"user_id": cognito_user_id})) is not None:
            return user

        log.info("No user found in reviews service.")
        return

    async def get_or_create(self, cognito_user_id: str, admin: bool = False):
        """Get or create user for reviews and ratings service.

        Args:
            cognito_user_id (str): User id provided by aws cognito fetched from bearer token
            email (Optional[EmailStr], optional): Email id of the user. Defaults to None.
            admin (bool, optional): [description]. Defaults to False.

        Returns:
            user (object): User object from database
        """
        if (user := await self._collection.find_one({"user_id": cognito_user_id})) is not None:
            return user

        log.info("No user found, creating new user")
        values = {
            "user_id": cognito_user_id,
            "user_role": UserTypeEnum.admin if admin else UserTypeEnum.user
        }
        user = await self.create(values)
        return user
