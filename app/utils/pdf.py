from pdfrw import PdfReader, PdfWriter, PdfString, PdfDict, PageMerge
from sqlalchemy.orm import Session
from models import ReceivingForm
from models.bookingForms_model import BookingForm
from fastapi import HTTPException
from config import BASE_DIR



def generate_receiving_form_pdf(db: Session, form_id: int):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "reception.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(ReceivingForm).filter(ReceivingForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Approved form not found")

    data = {
        "day": form.day,
        "current_date": str(form.current_date),
        "customer_name": form.customer_name,
        "receive_date": str(form.receive_date),
        "customer_phone_number": form.customer_phone_number,
        "brand": form.brand,
        "model": form.model,
        "color": form.color,
        "chassis_number": form.chassis_number,
        "plate_number": form.plate_number,
        "mileage": str(form.mileage),
        "category": form.category,
        "fix_description": form.fix_description,
        "total_price": str(form.total_price),
        "remains": str(form.remains),
        "total_paid": str(form.total_paid),
        "notes": form.notes,
        "employee_name": form.employee_name,
    }

    template_pdf = PdfReader(str(TEMPLATE_PATH))

    if not template_pdf.Root.AcroForm:
        template_pdf.Root.AcroForm = PdfDict()

    template_pdf.Root.AcroForm.update(
        PdfDict(NeedAppearances=PdfDict(indirect=True))
    )

    def fill_field(field):
        if field.T:
            name = field.T.to_unicode()
            if name in data:
                field.V = PdfString.encode(str(data[name]))
                field.AP = None

                field.Ff = 1

                field.update(
                    PdfDict(
                        F=4,
                        BS=PdfDict(W=0),
                        MK=PdfDict(BC=[], BG=[]),
                    )
                )

        if field.Kids:
            for kid in field.Kids:
                fill_field(kid)

    for field in template_pdf.Root.AcroForm.Fields:
        fill_field(field)

    output_path = OUTPUT_DIR / f"receiving_form_{form.id}.pdf"
    PdfWriter().write(output_path, template_pdf)
    return {"url": f"/static/receiving_form_{form.id}.pdf"}

def generate_booking_form_pdf(db: Session, form_id: int):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "booking.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(BookingForm).filter(BookingForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Booking form not found")

    data = {
        "day": form.day,
        "current_date": str(form.current_date),
        "customer_name": form.customer_name,
        "receive_date": str(form.receive_date),
        "customer_phone_number": form.customer_phone_number,
        "brand": form.brand,
        "model": form.model,
        "color": form.color,
        "chassis_number": form.chassis_number,
        "plate_number": form.plate_number,
        "mileage": str(form.mileage),
        "category": form.category,
        "fix_description": form.fix_description,
        "total_price": str(form.total_price),
    }

    template_pdf = PdfReader(str(TEMPLATE_PATH))

    if not template_pdf.Root.AcroForm:
        template_pdf.Root.AcroForm = PdfDict()

    template_pdf.Root.AcroForm.update(
        PdfDict(NeedAppearances=PdfDict(indirect=True))
    )

    def fill_field(field):
        if field.T:
            name = field.T.to_unicode()
            if name in data:
                field.V = PdfString.encode(str(data[name]))
                field.AP = None

                field.Ff = 1

                field.update(
                    PdfDict(
                        F=4,
                        BS=PdfDict(W=0),
                        MK=PdfDict(BC=[], BG=[]),
                    )
                )

        if field.Kids:
            for kid in field.Kids:
                fill_field(kid)

    for field in template_pdf.Root.AcroForm.Fields:
        fill_field(field)

    output_path = OUTPUT_DIR / f"booking_form_{form.id}.pdf"
    PdfWriter().write(output_path, template_pdf)

    return {"url": f"/static/booking_form_{form.id}.pdf"}