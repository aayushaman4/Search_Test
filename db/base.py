from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import log, settings
from starlette.requests import Request


class DataBase:
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        str(settings.mongo_db_url),
        maxPoolSize=settings.db_pool_max_size, minPoolSize=settings.db_pool_min_size)


db = DataBase()


def get_db_client() -> AsyncIOMotorClient:
    return db.client


def get_database(request: Request):
    """Get current database from app state.

    Args:
        request (Request): HTTP Request object through API.

    Returns:
        Database: Apps database.
    """
    return request.app.mongodb


async def connect_to_mongo(app: FastAPI):
    try:
        log.info("connecting to mongo database...")
        app.mongodb_client = get_db_client()
        app.mongodb = app.mongodb_client[settings.db_name]
        log.info("mongo database connected!")

    except Exception as err:
        log.warn("--- DB CONNECTION ERROR ---")
        log.error(err)
        log.warn("--- DB CONNECTION ERROR ---")


async def close_mongo_connection(app: FastAPI):
    try:
        log.info("closing mongo database connection...")
        app.mongodb_client.close()
        db.client.close()
        log.info("mongo database disconnected!")

    except Exception as err:
        log.warn("--- DB DISCONNECT ERROR ---")
        log.error(err)
        log.warn("--- DB DISCONNECT ERROR ---")
