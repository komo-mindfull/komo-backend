from time import sleep
from fastapi import FastAPI
from . import models
from .database import engine
from .routers.users import router as user_route
from .routers.auth import router as auth_route
from .routers.journal import router as journal_router
from .config import envar


while True:
    try:
        models.Base.metadata.create_all(bind=engine)
        break
    except Exception as error:
        print("Connection failed: ", error)
        sleep(2)

app = FastAPI()

app.include_router(user_route)
app.include_router(auth_route)
app.include_router(journal_router)


@app.get('/')
def root():
    return {"messages": "Hello World"}
