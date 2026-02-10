from fastapi import FastAPI
from database import engine
from app.models import employees, cars, customers
from app.database import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)
