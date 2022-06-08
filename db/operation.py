from pydantic import ListError
from db.schemas import MovieCreate, Movie, MovieOut, MovieUpdate
from db.repository import BaseRepository
from core.constants import Collections
from typing import Type

class MovieOperation(BaseRepository):
    @property
    def _db_collection(self):
        return Collections.pixel_tracker

    @property
    def _schema_out(self) -> Type[MovieOut]:
        return MovieOut

    @property
    def _schema_create(self) -> Type[MovieCreate]:
        return MovieCreate

    @property
    def _schema_update(self) -> Type[MovieUpdate]:
        return MovieUpdate

    async def FilterData(self, query: str):
        # document_count: int = await self._count_documents()
        # cursor = self._collection.aggregate([{"$search": 
        # {"compound": 
        # {"index" : "detail", "filter": [{"text": {"query": query.split(" "),"path": {"value": "Title", "det": "Title"}}}]
        # }
        # }}])
        # return await cursor.to_list(document_count)
        pass

