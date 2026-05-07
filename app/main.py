from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from app.database import engine, Base
from app.routers import admin, cars, employees, login, manager, comparison, receiving, prices_description, sales, receptionist, customers, customer_support, booking, representative, appointments, delivery, reports, accountant, vip, send_whatsapp, salary
from app.models import attendance_model, employees_model, cars_model, customers_model, description_model, prices_model, receivingForms_model, bookingForms_model, appointments_model, comparisonForms_model, deliveryForms_model
from app.config import BASE_DIR

load_dotenv()

templates = Jinja2Templates(directory=BASE_DIR / "templates")

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
app.include_router(sales.router)
app.include_router(receptionist.router)
app.include_router(customers.router)
app.include_router(customer_support.router)
app.include_router(booking.router)
app.include_router(representative.router)
app.include_router(appointments.router)
app.include_router(delivery.router)
app.include_router(accountant.router)
app.include_router(reports.router)
app.include_router(vip.router)
app.include_router(send_whatsapp.router)
app.include_router(salary.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})