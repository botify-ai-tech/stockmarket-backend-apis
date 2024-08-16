import uvicorn
from fastapi import FastAPI
from main import run


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/backtest")
def share_details():
    data = run()
    return data


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)