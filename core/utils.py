import uuid
from typing import Optional

from bson.objectid import ObjectId
from fastapi import HTTPException, status
from core.config import log, settings


def fix_obj_id(document: any):
    document["_id"] = str(document["_id"])
    return document


def validate_object_id(id: str):
    try:
        _id = ObjectId(id)
    except Exception:
        if settings.debug:
            log.warning("Invalid Object ID")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Object ID")
    return _id


def generate_uuid():
    """Function to generate uuid for unique id fields.

    Returns:
        str: Generated unique uuid.
    """
    return str(uuid.uuid4())


def generate_random_filename(file_format: str = "png"):
    """Generate random file name with format as string.

    Args:
        file_format (str, optional): Type of file format. Defaults to "png".

    Returns:
        filename (str): Random file name with format specified.
    """
    log.info(f"Generating random string {file_format}")
    return uuid.uuid4().hex[:6].upper().replace('0', 'X').replace('O', 'Y') + '.' + file_format.lower()


async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 10):
    """Common Request query parameters.

    Args:
        q (Optional[str], optional): [description]. Defaults to None.
        skip (int, optional): [description]. Defaults to 0.
        limit (int, optional): [description]. Defaults to 100.

    Returns:
        dict: Query Parameters for GET requests to apply pagination.
    """
    return {"q": q, "skip": skip, "limit": limit}
