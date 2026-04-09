from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date

def calculate_parts_daily(db: Session, dbModel):
    rows = db.query(
        dbModel.buying_price,
        dbModel.selling_price,
        dbModel.revenue
    ).filter(
        dbModel.current_date == date.today(),
        dbModel.revenue.isnot(None)
    ).all()

    totals = db.query(
        func.sum(dbModel.buying_price),
        func.sum(dbModel.selling_price),
        func.sum(dbModel.revenue)
    ).filter(
        dbModel.current_date == date.today(),
        dbModel.revenue.isnot(None)
    ).first()

    return {
        "rows": [
            {
                "buying_price": r.buying_price,
                "selling_price": r.selling_price,
                "revenue": r.revenue
            }
            for r in rows
        ],
        "total_buying": totals[0],
        "total_selling": totals[1],
        "total_revenue": totals[2]
    }

def calculate_parts_monthly(db: Session, dbModel):
    today = date.today()
    start_of_month = today.replace(day=1)
    rows = db.query(
        dbModel.buying_price,
        dbModel.selling_price,
        dbModel.revenue
    ).filter(
        dbModel.current_date >= start_of_month,
        dbModel.current_date <= today,
        dbModel.revenue.isnot(None)
    ).all()

    totals = db.query(
        func.sum(dbModel.buying_price),
        func.sum(dbModel.selling_price),
        func.sum(dbModel.revenue)
    ).filter(
        dbModel.current_date >= start_of_month,
        dbModel.current_date <= today,
        dbModel.revenue.isnot(None)
    ).first()

    for r in rows:
        print("BUY:", r.buying_price, "SELL:", r.selling_price, "REV:", r.revenue)

    return {
        "rows": [
            {
                "buying_price": r.buying_price,
                "selling_price": r.selling_price,
                "revenue": r.revenue
            }
            for r in rows
        ],
        "total_buying": totals[0],
        "total_selling": totals[1],
        "total_revenue": totals[2]
    }

def calculate_parts_yearly(db: Session, dbModel):
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    rows = db.query(
        dbModel.buying_price,
        dbModel.selling_price,
        dbModel.revenue
    ).filter(
        dbModel.current_date >= start_of_year,
        dbModel.current_date <= today,
        dbModel.revenue.isnot(None)
    ).all()

    totals = db.query(
        func.sum(dbModel.buying_price),
        func.sum(dbModel.selling_price),
        func.sum(dbModel.revenue)
    ).filter(
        dbModel.current_date >= start_of_year,
        dbModel.current_date <= today,
        dbModel.revenue.isnot(None)
    ).first()

    return {
        "rows": [
            {
                "buying_price": r.buying_price,
                "selling_price": r.selling_price,
                "revenue": r.revenue
            }
            for r in rows
        ],
        "total_buying": totals[0],
        "total_selling": totals[1],
        "total_revenue": totals[2]
    }


def calculate_daily(db: Session, dbModel):

    rows = db.query(dbModel.total_price, dbModel.current_date).filter(
        dbModel.current_date == date.today(),
        dbModel.approved.is_(True)
    ).all()

    # Calculate total
    total = db.query(func.coalesce(func.sum(dbModel.total_price), 0)).filter(
        dbModel.current_date == date.today(),
        dbModel.approved.is_(True)
    ).scalar()

    return {
        "rows": [
        {
            "total_price": r.total_price,
            "current_date": r.current_date
        }
        for r in rows
    ],
        "total": total
    }


def calculate_monthly(db: Session, dbModel):
    today = date.today()
    start_of_month = today.replace(day=1)

    rows = db.query(dbModel.total_price, dbModel.current_date).filter(
        dbModel.current_date >= start_of_month,
        dbModel.current_date <= today,
        dbModel.approved.is_(True)
    ).all()

    total = db.query(func.coalesce(func.sum(dbModel.total_price), 0)).filter(
        dbModel.current_date >= start_of_month,
        dbModel.current_date <= today,
        dbModel.approved.is_(True)
    ).scalar()

    return {
        "rows": [
        {
            "total_price": r.total_price,
            "current_date": r.current_date
        }
        for r in rows
    ],
        "total": total
    }


def calculate_yearly(db: Session, dbModel):
    today = date.today()
    start_of_year = date(today.year, 1, 1)

    rows = db.query(dbModel.total_price, dbModel.current_date).filter(
        dbModel.current_date >= start_of_year,
        dbModel.current_date <= today,
        dbModel.approved.is_(True)
    ).all()

    total = db.query(func.coalesce(func.sum(dbModel.total_price), 0)).filter(
        dbModel.current_date >= start_of_year,
        dbModel.current_date <= today,
        dbModel.approved.is_(True)
    ).scalar()

    return {
        "rows": [
        {
            "total_price": r.total_price,
            "current_date": r.current_date
        }
        for r in rows
    ],
        "total": total
    }