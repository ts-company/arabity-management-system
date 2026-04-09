from reportlab.pdfgen import canvas
from reportlab.lib import colors
from pdfrw import PdfReader, PdfWriter, PageMerge
from io import BytesIO
from sqlalchemy.orm import Session
from models.receivingForms_model import ReceivingForm
from models.bookingForms_model import BookingForm
from models.comparisonForms_model import ComparisonForm
from models.deliveryForms_model import DeliveryForm
from fastapi import HTTPException
from config import BASE_DIR
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
import re
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


pdfmetrics.registerFont(
    TTFont("CustomFont", str(BASE_DIR / "static" / "fonts" / "arial.ttf"))
)


def is_arabic(text):
    if not text:
        return False
    arabic_range = re.compile(r'[\u0600-\u06FF]')
    return arabic_range.search(text) is not None


def format_text(text):
    if not text:
        return ""

    if is_arabic(text):
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        return bidi_text
    else:
        return str(text)


def draw_smart_text(can, x, y, text, field_width=None, base_font_size=15):
    formatted = format_text(text)

    if not formatted:
        return

    font_name = "CustomFont"
    font_size = base_font_size
    can.setFont(font_name, font_size)

    if field_width:
        text_width = can.stringWidth(formatted, font_name, font_size)

        while text_width > field_width and font_size > 6:
            font_size -= 1
            can.setFont(font_name, font_size)
            text_width = can.stringWidth(formatted, font_name, font_size)

    if is_arabic(text):
        if field_width:
            can.drawRightString(x + field_width, y, formatted)
        else:
            can.drawRightString(x, y, formatted)
    else:
        can.drawString(x, y, formatted)

def draw_multiline_text(can, x, y, text, field_width, field_height, font_size=15):
    formatted = format_text(text)
    if not formatted:
        return
    is_ar = is_arabic(text)
    alignment = TA_RIGHT if is_ar else TA_LEFT
    style = ParagraphStyle(
        name='Normal',
        fontName='CustomFont',
        fontSize=font_size,
        leading=font_size + 4,
        textColor=colors.black,
        alignment=alignment,
    )
    p = Paragraph(formatted, style)
    w, h = p.wrap(field_width, field_height)
    p.drawOn(can, x, y - h)

def draw_checkbox(can, x, y, size=12):
    can.setFont("CustomFont", size)
    can.drawCentredString(x, y - (size / 3), "✓")

def generate_receiving_form_pdf(db: Session, form_id: int):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "reception.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(ReceivingForm).filter(ReceivingForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    output_path = OUTPUT_DIR / f"receiving_form_{form.id}.pdf"
    template_pdf = PdfReader(str(TEMPLATE_PATH))
    page = template_pdf.pages[0]

    width = float(page.MediaBox[2])
    height = float(page.MediaBox[3])

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("CustomFont", 15)

    draw_smart_text(can, 400, 709, form.day, field_width=120)
    draw_smart_text(can, 210, 709, str(form.current_date), field_width=100)
    draw_smart_text(can, 290, 675, form.customer_name, field_width=200)
    draw_smart_text(can, 90, 675, str(form.receive_date), field_width=80)
    draw_smart_text(can, 410, 640, form.customer_phone_number, field_width=90)
    draw_smart_text(can, 250, 640, form.brand, field_width=80)
    draw_smart_text(can, 130, 640, form.model, field_width=60)
    draw_smart_text(can, 40, 640, form.color, field_width=50)
    draw_smart_text(can, 410, 600, form.chassis_number, field_width=90)
    draw_smart_text(can, 230, 600, form.plate_number, field_width=70)
    draw_smart_text(can, 60, 600, str(form.mileage), field_width=80)
    draw_multiline_text(can, 460, 525, ' '.join(form.category), field_width=90, field_height=175, font_size=13)
    draw_multiline_text(can, 250, 525, form.fix_description, field_width=90, field_height=175, font_size=13)
    draw_smart_text(can, 70, 513, str(form.total_price), field_width=80)
    draw_smart_text(can, 380, 277, str(form.total_price), field_width=140)
    draw_smart_text(can, 70, 270, str(form.remains), field_width=100)
    draw_smart_text(can, 320, 250, str(form.total_paid), field_width=120)
    if form.payment_method == "cash":
        draw_checkbox(can, 113, 93)
    elif form.payment_method == "visa":
        draw_checkbox(can, 44, 93)
    elif form.payment_method == "instapay":
        draw_checkbox(can, 189, 93)
    draw_smart_text(can, 60, 210, form.notes, field_width=380)
    draw_smart_text(can, 40, 132, form.national_id, field_width=130)
    draw_smart_text(can, 320, 105, form.employee_name, field_width=140)

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    PageMerge(page).add(overlay_pdf.pages[0]).render()
    PdfWriter().write(str(output_path), template_pdf)

    return f"/static/receiving_form_{form.id}.pdf"

def generate_booking_form_pdf(db: Session, form_id: int):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "booking.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(BookingForm).filter(BookingForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    output_path = OUTPUT_DIR / f"booking_form_{form.id}.pdf"
    template_pdf = PdfReader(str(TEMPLATE_PATH))
    page = template_pdf.pages[0]

    width = float(page.MediaBox[2])
    height = float(page.MediaBox[3])

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("CustomFont", 15)

    draw_smart_text(can, 400, 709, form.day, field_width=120)
    draw_smart_text(can, 210, 709, str(form.current_date), field_width=100)
    draw_smart_text(can, 290, 670, form.customer_name, field_width=200)
    draw_smart_text(can, 100, 670, str(form.receive_date), field_width=80)
    draw_smart_text(can, 410, 639, form.customer_phone_number, field_width=100)
    draw_smart_text(can, 250, 639, form.brand, field_width=90)
    draw_smart_text(can, 130, 639, form.model, field_width=60)
    draw_smart_text(can, 40, 639, form.color, field_width=50)
    draw_smart_text(can, 400, 600, form.chassis_number, field_width=100)
    draw_smart_text(can, 220, 600, form.plate_number, field_width=80)
    draw_smart_text(can, 60, 600, str(form.mileage), field_width=80)
    draw_smart_text(can, 420, 500, form.category, field_width=120)
    draw_multiline_text(can, 230, 510, form.fix_description, field_width=140, field_height=160, font_size=13)
    draw_smart_text(can, 60, 500, str(form.total_price), field_width=120)
    if form.payment_method == "cash":
        draw_checkbox(can, 144, 99)
    elif form.payment_method == "visa":
        draw_checkbox(can, 80, 99)

    draw_smart_text(can, 340, 135, str(form.employee_name), field_width=140)

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    PageMerge(page).add(overlay_pdf.pages[0]).render()
    PdfWriter().write(str(output_path), template_pdf)
    return f"/static/booking_form_{form.id}.pdf"


def generate_comparison_form_pdf(db: Session, form_id: int):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "comparison.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(ComparisonForm).filter(ComparisonForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    output_path = OUTPUT_DIR / f"comparison_form_{form.id}.pdf"
    template_pdf = PdfReader(str(TEMPLATE_PATH))
    page = template_pdf.pages[0]

    width = float(page.MediaBox[2])
    height = float(page.MediaBox[3])

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("CustomFont", 15)

    draw_smart_text(can, 390, 699, form.day, field_width=130)
    draw_smart_text(can, 190, 699, str(form.current_date), field_width=120)
    draw_smart_text(can, 300, 660, form.customer_name, field_width=190)
    draw_smart_text(can, 80, 660, str(form.receive_date), field_width=90)
    draw_smart_text(can, 410, 629, form.customer_phone_number, field_width=90)
    draw_smart_text(can, 250, 629, form.brand, field_width=90)
    draw_smart_text(can, 130, 629, form.model, field_width=60)
    draw_smart_text(can, 40, 629, form.color, field_width=50)
    draw_smart_text(can, 400, 590, form.chassis_number, field_width=100)
    draw_smart_text(can, 220, 590, form.plate_number, field_width=80)
    draw_smart_text(can, 60, 590, str(form.mileage), field_width=80)
    draw_smart_text(can, 420, 485, form.category, field_width=120)
    draw_multiline_text(can, 230, 490, form.fix_description, field_width=140, field_height=160, font_size=13)
    draw_smart_text(can, 60, 485, str(form.total_price), field_width=120)
    if form.payment_method == "cash":
        draw_checkbox(can, 144, 99)
    elif form.payment_method == "visa":
        draw_checkbox(can ,80, 99)
    draw_smart_text(can, 370, 250, str(form.total_price), field_width=140)
    draw_smart_text(can, 420, 150, str(form.employee_name), field_width=130)

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    PageMerge(page).add(overlay_pdf.pages[0]).render()
    PdfWriter().write(str(output_path), template_pdf)
    return f"/static/comparison_form_{form.id}.pdf"

def generate_delivery_form_pdf(db: Session, form_id: int):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "delivery.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(DeliveryForm).filter(DeliveryForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    output_path = OUTPUT_DIR / f"delivery_form_{form.id}.pdf"
    template_pdf = PdfReader(str(TEMPLATE_PATH))
    page = template_pdf.pages[0]

    width = float(page.MediaBox[2])
    height = float(page.MediaBox[3])

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("CustomFont", 15)

    draw_smart_text(can, 390, 690, form.day, field_width=120)
    draw_smart_text(can, 190, 690, str(form.current_date), field_width=110)
    draw_smart_text(can, 310, 650, form.customer_name, field_width=180)
    draw_smart_text(can, 80, 650, str(form.receive_date), field_width=90)
    draw_smart_text(can, 410, 620, form.customer_phone_number, field_width=100)
    draw_smart_text(can, 240, 620, form.brand, field_width=100)
    draw_smart_text(can, 130, 620, form.model, field_width=70)
    draw_smart_text(can, 40, 620, form.color, field_width=50)
    draw_smart_text(can, 400, 580, form.chassis_number, field_width=100)
    draw_smart_text(can, 220, 580, form.plate_number, field_width=80)
    draw_smart_text(can, 60, 580, str(form.mileage), field_width=80)
    draw_smart_text(can, 410, 170, str(form.employee_name), field_width=130)

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    PageMerge(page).add(overlay_pdf.pages[0]).render()
    PdfWriter().write(str(output_path), template_pdf)
    return f"/static/delivery_form_{form.id}.pdf"

def generate_warranty_pdf(db: Session, form_id: int, dbModel):
    TEMPLATE_PATH = BASE_DIR / "static" / "templates" / "warranty.pdf"
    OUTPUT_DIR = BASE_DIR / "static"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    form = db.query(dbModel).filter(dbModel.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    output_path = OUTPUT_DIR / f"warranty_form_{form.id}.pdf"
    template_pdf = PdfReader(str(TEMPLATE_PATH))
    page = template_pdf.pages[0]

    width = float(page.MediaBox[2])
    height = float(page.MediaBox[3])

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("CustomFont", 15)

    draw_smart_text(can, 310, 650, form.customer_name, field_width=180)
    draw_smart_text(can, 410, 620, form.customer_phone_number, field_width=100)
    draw_smart_text(can, 240, 620, form.brand, field_width=100)
    draw_smart_text(can, 130, 620, form.model, field_width=70)
    draw_smart_text(can, 400, 580, form.chassis_number, field_width=100)
    draw_smart_text(can, 220, 580, form.plate_number, field_width=80)
    draw_smart_text(can, 220, 580, form.period, field_width=80)
    draw_smart_text(can, 220, 580, str(form.start_date), field_width=80)
    draw_smart_text(can, 190, 690, str(form.current_date), field_width=110)

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    PageMerge(page).add(overlay_pdf.pages[0]).render()
    PdfWriter().write(str(output_path), template_pdf)
    return f"/static/warranty_form_{form.id}.pdf"

def generate_coordinate_grid():
    TEMPLATE_PATH = "comparison.pdf"
    OUTPUT_PATH = "comparison_grid_preview.pdf"

    template_pdf = PdfReader(TEMPLATE_PATH)
    page = template_pdf.pages[0]

    width = float(page.MediaBox[2])
    height = float(page.MediaBox[3])

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    can.setFont("Helvetica", 6)
    can.setStrokeColorRGB(0.85, 0.85, 0.85)
    can.setFillColor(colors.red)

    spacing = 10

    for x in range(0, int(width), spacing):
        can.line(x, 0, x, height)
        can.drawString(x + 2, 2, str(x))

    for y in range(0, int(height), spacing):
        can.line(0, y, width, y)
        can.drawString(2, y + 2, str(y))

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    PageMerge(page).add(overlay_pdf.pages[0]).render()

    PdfWriter().write(OUTPUT_PATH, template_pdf)