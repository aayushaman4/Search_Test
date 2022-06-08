from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi.param_functions import Body
from core.mixins import BaseSchema, DateTimeModelMixin, IDModelMixin


class Movie(BaseSchema):
    Source: Optional[Dict[str, Any]] 
    Id : Optional[str]
    is_processed : Optional[bool]
    is_cdn_processed : Optional[bool]
    is_deeplink_processed : Optional[bool]
    is_id_processed : Optional[bool]

class MovieCreate(Movie):
    pass

class MovieUpdate(Movie):
    pass

class MovieInDb(Movie, DateTimeModelMixin, IDModelMixin):
    pass

class MovieOut(MovieInDb):
    pass
