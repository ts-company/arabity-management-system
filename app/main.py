from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
# from app.routers import employees, customers, auth
from app.models import employees
from app.models import cars


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


# Routers
# app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# app.include_router(employees.router, prefix="/employees", tags=["Employees"])
# app.include_router(customers.router, prefix="/customers", tags=["Customers"])