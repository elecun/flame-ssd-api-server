from typing import Union
from celery import Celery
from fastapi import FastAPI

app = FastAPI()

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@celery.task
def divide(x, y):
    import time
    time.sleep(5)
    return x / y