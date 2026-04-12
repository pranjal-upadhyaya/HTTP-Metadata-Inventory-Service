import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def startup():
    return {
        "status": 200,
        "message": "Successfull startup"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)