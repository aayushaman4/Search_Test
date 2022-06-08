from typing import Callable

from fastapi import FastAPI
from src.db.base import close_mongo_connection, connect_to_mongo
from src.v1.helpers import (trigger_update_product_ratings_and_review_Count,
                            delete_s3_uploads_which_is_greater_then_30min)
from src.RatingsAndReviews.indexing_curd import create_db_indexes
from src.core.config import settings


def create_start_app_handler(app: FastAPI) -> Callable:
    """Decorator to handle app startup event along with DB connection.

    Returns:
        start_app (DB connected App Object)
    """

    async def start_app() -> None:
        await connect_to_mongo(app)
        await create_db_indexes()
        if settings.active_scheduler:
            await trigger_update_product_ratings_and_review_Count()
            await delete_s3_uploads_which_is_greater_then_30min()
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """Decorator to handle app shutdown event after closed DB connection.

    Returns:
        stop_app (DB disconnect App Object)
    """

    async def stop_app() -> None:
        await close_mongo_connection(app)
    return stop_app
