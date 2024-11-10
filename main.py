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
page_type = ''

def print_customer_detail(c, y_position, report_data):
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
    return y_position

def print_header(c, y_position, width, parameter):

    # TEST NAME OBSERVED VALUE UNITS Bio. Ref. Interval.
    # Investigation Details Header
    c.setFont("Helvetica-Bold", 12)
    if parameter == 'P1':
        # Draw a horizontal line
        c.line(25, y_position - 5, width - 30, y_position - 5)
        y_position -= 20
        c.drawString(10, y_position, "TEST NAME")
        c.drawString(340, y_position, "OBSERVED VALUE")
        c.drawString(464, y_position, "UNITS")
        c.drawString(509, y_position, "Bio. Ref. Interval.")
        c.line(25, y_position - 5, width - 30, y_position - 5)

    elif parameter == 'P2':
        # Draw a horizontal line
        c.line(25, y_position - 5, width - 30, y_position - 5)
        y_position -= 20
        c.drawString(10, y_position, "TEST NAME")
        c.drawString(340, y_position, "TECHNOLOGY")
        c.drawString(464, y_position, "VALUE")
        c.drawString(509, y_position, "UNITS")

        c.line(25, y_position - 5, width - 30, y_position - 5)
    elif parameter == 'P3':
        # Draw a horizontal line
        c.line(25, y_position - 5, width - 30, y_position - 5)
        y_position -= 20
        c.drawString(10, y_position, "TEST NAME")
        c.drawString(240, y_position, "TECHNOLOGY")
        c.drawString(360, y_position, "VALUE")
        c.drawString(460, y_position, "UNITS")
        c.drawString(509, y_position, "Bio. Ref. Interval.")
        c.line(25, y_position - 5, width - 30, y_position - 5)

    y_position -= 20
    return y_position

def page_type_1(c, y_position, test):
    # Reset font for values
    # c.setFont("Helvetica-Bold", 14)
    c.setFont("Times-Roman", 12)
    c.drawString(10, y_position, test.get('name', ''))
    # c.setFont("Times-Roman", 12)
    observations = test.get('observations', [])
    if len(observations) == 0:
        if test.get('technology', False) and test.get('value', False) and test.get('unit', False) and test.get('reference_range', False):
            c.drawString(240, y_position, test.get('technology', ''))
            c.drawString(360, y_position, test.get('value', ''))
            c.drawString(460, y_position, test.get('unit', ''))
            c.drawString(509, y_position, test.get('reference_range', ''))
        elif test.get('value', False) and test.get('unit', False) and test.get('reference_range', False):
            c.drawString(340, y_position, test.get('value', ''))
            c.drawString(464, y_position, test.get('unit', ''))
            c.drawString(509, y_position, test.get('reference_range', ''))
        elif test.get('technology', False) and test.get('value', False) and test.get('unit', False):
            c.drawString(340, y_position, test.get('technology', ''))
            c.drawString(464 , y_position, test.get('value', ''))
            c.drawString(509, y_position, test.get('unit', ''))
        y_position -= 10
    else:
        y_position -= 10
        for observation in observations:
            # Reset font for values
            c.setFont("Times-Roman", 12)

            c.drawString(10, y_position, observation.get('name', ''))
            c.drawString(340, y_position, observation.get('value', ''))
            c.drawString(464, y_position, observation.get('unit', ''))
            c.drawString(509, y_position, observation.get('reference_range', ''))
            y_position -= 10
        y_position -= 10
    return y_position

def horizontal_line(c, y_position, max_text_width,text):
    c.drawString(10, y_position, text)
    y_position -= 2
    c.line(20, y_position - 5, max_text_width+15, y_position)
    y_position -= 10

    return y_position

def print_notes(c, y_position, notes, max_text_width):
    # [{"notes_name":"Bio. Ref. Interval.", "details": ["DEFICIENCY : <20 ng/ml || INSUFFICIENCY : 20-<30 ng/ml", "SUFFICIENCY : 30-100 ng/ml || TOXICITY : >100 ng/ml"]}]
    print(notes)
    # len1 = len(notes)
    # for i in range(0, len1):

    for note in notes:
        print(note, 'j')

        c.drawString(10, y_position, note.get('notes_name', ''))
        y_position -= 10
        for detail in note.get('details', []):
            y_position = draw_wrapped_text(c, 10, y_position, detail, max_text_width)
            # c.drawString(10, y_position, detail)
            y_position -= 10

    y_position -= 10
    return y_position


def draw_wrapped_text(c, x_position, y_position, detail, max_width):
    # Break detail text into lines that fit within max_width
    text_lines = []
    words = detail.split()
    line = ""

    for word in words:
        # Add the word to the line temporarily to check if it fits
        test_line = f"{line} {word}".strip()
        # Calculate the width of the test line
        if c.stringWidth(test_line, "Times-Roman", 12) <= max_width:
            # If it fits, add the word to the line
            line = test_line
        else:
            # If it doesn't fit, add the line to text_lines and start a new line
            text_lines.append(line)
            line = word  # Start a new line with the current word
    text_lines.append(line)  # Add the last line

    # Draw each line on the canvas
    for line in text_lines:
        c.drawString(x_position, y_position, line)
        y_position -= 14  # Move down for the next line (adjust as needed)

    return y_position  # Return the updated y_position


def generate_pdf(report_data):


    # Use BytesIO to create a binary stream for the PDF
    pdf_buffer = BytesIO()

    # Create a PDF using ReportLab
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    max_text_width = width - 40  # Set a max width for the text area

    # Set initial y position
    y_position = height - 150
    y_position = print_customer_detail(c,y_position, report_data)


    # Add investigation details
    tests = report_data.get('tests', [])
    for test in tests:

        if test.get('horizontal_line', False):
            y_position = horizontal_line(c, y_position, max_text_width, test.get('text', ''))
        new_page_type = test.get('page_type', '')
        if new_page_type:
            page_type = new_page_type
        if test.get('new_page', False):
            y_position -= 10
            c.line(25, y_position - 5, width - 30, y_position - 5)
            c.showPage()
            y_position = height - 150
            y_position = print_customer_detail(c, y_position, report_data)

        y_position = print_header(c, y_position, width, test.get('page_type'))

        if page_type == "P1":
            try:
                y_position = page_type_1(c, y_position, test)
            except:
                print("error in printing page")
        elif page_type == "P2" or page_type == "P3":
            try:
                y_position = page_type_1(c, y_position, test)
                notes = test.get('notes', [])
                if len(notes) != 0:
                    y_position = print_notes(c, y_position, notes, max_text_width)
            except:
                print("error printing page")


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
        pdf_buffer = generate_pdf(report_data)
        return StreamingResponse(pdf_buffer, media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=report.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# To run the FastAPI application, use the command:
# uvicorn main:app --reload
