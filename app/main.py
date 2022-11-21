from http.client import HTTPException
from time import sleep
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine, get_db
from .routers.users import router as user_route
from .routers.auth import router as auth_route
from .routers.journal import router as journal_router
from .routers.expert import router as expert_router
from .oAuth2 import get_current_user


while True:
    try:
        models.Base.metadata.create_all(bind=engine)
        break
    except Exception as error:
        print("Connection failed: ", error)
        sleep(2)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_route)
app.include_router(auth_route)
app.include_router(journal_router)
app.include_router(expert_router)


@app.get("/")
def root():
    return {"messages": "Hello World"}

@app.get("/currentuser")
def current_user(db : Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    curr_user = db.query(models.User).filter(models.User.id == current_user).first()
    if not curr_user:
        raise HTTPException(status_code=404, detail="User not found")
    curr_user.password = None
    return curr_user
