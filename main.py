from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello world"}


@app.get("/items")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "query": q}
