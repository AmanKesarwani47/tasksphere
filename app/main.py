from fastapi import FastAPI
from app.database import Base, engine
from app.routers import users, tasks, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskSphere Backend")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)