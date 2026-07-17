from flask import Blueprint, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

report_bp = Blueprint("report", __name__)

@report_bp.route("/report")
def report():
    # PDF ke liye buffer create karo
    buffer = BytesIO()

    # PDF canvas create karo, size letter (8.5x11 inch)
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 50, "SkillCheck Report")

    # Some sample content
    c.setFont("Helvetica", 12)
    y = height - 100
    lines = [
        "Name: Jamirahmad Mulani",
        "User ID: 1",
        "Score: 85",
        "Status: Passed",
        "",
        "Thank you for taking the SkillCheck Test!"
    ]

    for line in lines:
        c.drawString(100, y, line)
        y -= 20  

    c.showPage()  
    c.save()     
    # Set buffer to start
    buffer.seek(0)

    # Send file as download
    return send_file(
        buffer,
        as_attachment=True,
        download_name="SkillCheck_Report.pdf",
        mimetype="application/pdf"
    )
