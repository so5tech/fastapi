from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (you can restrict this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def generate_pdf(report_data):
    # Use BytesIO to create a binary stream for the PDF
    pdf_buffer = BytesIO()

    # Create a PDF using ReportLab
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Set initial y position
    y_position = height - 150

    # Set font to a specific type and size
    c.setFont("Times-Roman", 12)

    # Draw content with vertical spacing
    c.drawString(100, y_position, f"Name: {report_data.get('name', '_____________________')}")
    y_position -= 20
    c.drawString(100, y_position, f"Referred By: {report_data.get('referred_by', '______________')}")
    y_position -= 20
    c.drawString(100, y_position, f"Collection Date: {report_data.get('collection_date', '___________')}")
    y_position += 20
    c.drawString(400, y_position, f"Age/Gender: {report_data.get('age_gender', '_______________')}")
    y_position -= 20
    c.drawString(400, y_position, f"Report Release Date: {report_data.get('report_release_date', '________')}")

    # Draw a horizontal line
    c.line(25, y_position - 5, width - 30, y_position - 5)
    y_position -= 30

    # Investigation Details Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Investigation")
    c.drawString(200, y_position, "Observed Value")
    c.drawString(375, y_position, "Unit")
    c.drawString(450, y_position, "Biological Ref. Interval")
    c.line(25, y_position - 5, width - 30, y_position - 5)

    y_position -= 20

    # Reset font for values
    c.setFont("Times-Roman", 12)

    # Add investigation details
    investigations = report_data.get('investigations', [])
    for test in investigations:
        c.drawString(50, y_position, test.get('name', ''))
        c.drawString(200, y_position, test.get('value', ''))
        c.drawString(375, y_position, test.get('unit', ''))
        c.drawString(450, y_position, test.get('reference_range', ''))
        y_position -= 10

    # Draw another horizontal line
    y_position -= 10
    c.line(25, y_position - 5, width - 30, y_position - 5)

    # Save the PDF to the buffer
    c.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer

    return pdf_buffer

@app.post("/generate-pdf/")
async def create_pdf(report_data: dict):
    try:
        print(report_data)
        pdf_buffer = generate_pdf(report_data)
        return StreamingResponse(pdf_buffer, media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=report.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# To run the FastAPI application, use the command:
# uvicorn my_fastapi_app:app --reload
