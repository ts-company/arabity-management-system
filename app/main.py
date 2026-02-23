from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import engine, Base
from routers import admin, cars, employees, login, manager, comparison, receiving, prices_description, accept_reception, sales, receptionist, customers, customer_support, booking
from models import employees_model, cars_model, customers_model, description_model, prices_model, receivingForms_model, bookingForms_model
from config import BASE_DIR

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Arabity System",
    version="1.0.0"
)

app.mount("/static",StaticFiles(directory=BASE_DIR / "static"), name="static",)

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
app.include_router(comparison.router)
app.include_router(receiving.router)
app.include_router(prices_description.router)
app.include_router(accept_reception.router)
app.include_router(sales.router)
app.include_router(receptionist.router)
app.include_router(customers.router)
app.include_router(customer_support.router)
app.include_router(booking.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})