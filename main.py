from typing import Union

from fastapi import FastAPI
from db.operation import MovieOperation
from core.utils import common_parameters

app = FastAPI()
test = MovieOperation()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/search")
async def search():
    a = {"skip": 0, "limit": 10}
    return await test.list(**a)