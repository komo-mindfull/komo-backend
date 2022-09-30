from time import sleep
from fastapi import FastAPI
from . import models
from .database import engine
from .routers.posts import router as post_route
from .routers.users import router as user_route
from .routers.auth import router as auth_route
from .config import envar


while True:
    try:
        models.Base.metadata.create_all(bind=engine)
        break
    except Exception as error:
        print("Connection failed: ", error)
        sleep(2)

app = FastAPI()

# app.include_router(post_route)
app.include_router(user_route)
app.include_router(auth_route)


@app.get('/')
def root():
    return {"messages": "Hello World"}
