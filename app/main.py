from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import engine, Base
from routers import admin, cars, employees, login, manager
from models import employees_model
from models import cars_model

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Arabity System",
    version="1.0.0"
)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(admin.router)
app.include_router(cars.router)
app.include_router(employees.router)
app.include_router(login.router)
app.include_router(manager.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})