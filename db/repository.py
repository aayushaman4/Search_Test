import abc
from datetime import datetime
from typing import Dict, List, Mapping, Union

from bson.objectid import ObjectId
from fastapi import HTTPException, status
from fastapi.datastructures import UploadFile
from motor.motor_asyncio import (AsyncIOMotorClient, AsyncIOMotorCollection,
                                 AsyncIOMotorDatabase,
                                 AsyncIOMotorGridFSBucket)
from core.config import log, settings
from core.mixins import BaseSchema
from core.utils import validate_object_id
from db.base import get_db_client
from db.schemas import Movie, MovieCreate, MovieOut, MovieInDb

# Declare DB client for base crud operations.
db_client: AsyncIOMotorClient = get_db_client()

class BaseRepository(abc.ABC):
    """Base repository for all database collections.

    Args:
        abc.ABC (Class): Abstract base class.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._db: AsyncIOMotorDatabase = db_client[settings.db_name]
        self._collection: AsyncIOMotorCollection = self._db[self._db_collection]
        self.gridfield: AsyncIOMotorGridFSBucket = AsyncIOMotorGridFSBucket(self._db)
        super()

    @property
    @abc.abstractmethod
    def _db_collection(self):
        pass

    @property
    @abc.abstractmethod
    def _schema_create(self):
        pass

    @property
    @abc.abstractmethod
    def _schema_update(self):
        pass

    @property
    @abc.abstractmethod
    def _schema_out(self):
        pass

    def _preprocess_create(self, values: Union[BaseSchema, Dict]) -> Dict:
        if isinstance(values, dict):
            values = self._schema_create(**values)

        values = dict(values)
        if values.get("created_at"):
            values["created_at"] = datetime.utcnow()
        return values

    def _preprocess_update(self, values: Union[BaseSchema, Dict]) -> Dict:
        if isinstance(values, dict):
            values = self._schema_update(**values)
        values = dict(values)
        if values.get("last_modified_at"):
            values["last_modified_at"] = datetime.utcnow()
        return values

    async def _count_documents(self) -> int:
        return await self._collection.count_documents({})

    async def _get_object_or_404(self, id: str) -> Mapping:
        _id: ObjectId = validate_object_id(id)
        if (document := await self._collection.find_one({"_id": _id})) is not None:
            return document
        log.warn(f"No Document with ObjectId { id } found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    async def _list(self, **kwargs) -> List[Mapping]:
        document_count: int = await self._count_documents()
        cursor = self._collection.find(kwargs['kwargs'])
        return await cursor.to_list(document_count)

    async def _paginated_list(self, limit: int, skip: int, **kwargs) -> List[Mapping]:
        document_count: int = await self._count_documents()
        cursor = self._collection.find(kwargs).limit(limit).skip(skip)
        return await cursor.to_list(document_count)

    async def _insert(self, values: dict):
        return await self._collection.insert_one(values)

    async def _update(self, id: str, values: dict):
        _id: ObjectId = validate_object_id(id)
        return await self._collection.update_one({"_id": _id}, {"$set": values})

    async def _delete_by_id(self, id: str):
        _id: ObjectId = validate_object_id(id)
        return await self._collection.delete_one({"_id": _id})

    async def count(self) -> int:
        """Fetch total count of objects in the collection.

        Returns:
            Document Count (int): Count of all document.
        """
        return await self._count_documents()

    async def fetch_by_id(self, id: str):
        """Fetch document object based on Object ID

        Args:
            id (str): Object ID as string.

        Returns:
            Result (dict): If object is found returns dictionary object.
        """
        return await self._get_object_or_404(id)

    async def fetch_by_attribute(self, attr: dict):
        """Fetch document object based on attributes

        Args:
            attr (dict): attr as a dict.

        Returns:
            Result (dict): If object is found returns dictionary object.
        """
        try:
            return await self._collection.find_one(attr)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Error while fetching oject by attribute")

    async def list(self, **kwargs):
        """Fetch list of documents based on limit if limit is 0 other wise based on limit and offset

        Returns:
            Documents (list): List of all found documents.
        """
        if "limit" in kwargs.keys() and kwargs["limit"] == 0:
            rows = await self._list()
        else:
            rows = await self._paginated_list(kwargs["limit"], kwargs["skip"])

        if kwargs.get('re'):
            return [MovieOut.parse_obj(dict(row.items())) for row in rows]
        return [self._schema_out(**dict(row.items())) for row in rows]

    async def create(self, values: Union[BaseSchema, Dict]) -> BaseSchema:
        """Add new document object based on Payload

        Args:
            values (Union[BaseSchema, Dict]): Request Payload for create

        Raises:
            HTTPException: Error 400 if inserted Object ID is None

        Returns:
            BaseSchema: Returns newly added document Object.
        """
        dict_values = self._preprocess_create(values)
        new_document = await self._insert(dict_values)
        if new_document.inserted_id:
            return await self._get_object_or_404(new_document.inserted_id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error while creating new object")

    async def update(self, id: str, values: Union[BaseSchema, Dict]) -> BaseSchema:
        """Updates object based on Object ID and Payload.

        Args:
            id (str): [description]
            values (Union[BaseSchema, Dict]): Request Payload for update

        Raises:
            HTTPException: Error 400 if modified count is not 1

        Returns:
            Updated Object (BaseSchema): Returns updated object or existing if values dict.
        """
        existing_document = await self._get_object_or_404(id)
        dict_values = self._preprocess_update(values)
        values = {k: v for k, v in dict_values.items() if v is not None}

        if len(values) >= 1:
            update_document = await self._update(id, values)
            if update_document.modified_count == 1:
                if (updated_object := await self._get_object_or_404(id)) is not None:
                    return updated_object
        return existing_document

    async def delete(self, id: str):
        """Delete document object based on Object ID

        Args:
            id (str): Object ID as string

        Raises:
            HTTPException: Error 400 if deleted count is 0

        Returns:
            Response (dict): Success Message for Object delete operation.
        """
        await self._get_object_or_404(id)
        document = await self._delete_by_id(id)
        if document.deleted_count:
            return {"msg": f"Object { id } deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Error while deleting document id: { id }")

    async def upload_file(self, file: UploadFile):
        """ Uploads file to MongoDB GridFS file system and returns ID to be stored with collection document """

        file_id = await self.gridfield.upload_from_stream(
            file.filename,
            file.file,
            chunk_size_bytes=255 * 1024 * 1024,  # default 255kB
            metadata={"contentType": file.content_type})
        return file_id
