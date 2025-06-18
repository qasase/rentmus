from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime, timedelta
from rent_utils import extract_info_from_pdf, create_new_rent_increase_docx, schedule_file_deletion
import uvicorn
import mammoth
from mammoth.transforms import paragraph
from weasyprint import HTML, CSS
from io import BytesIO
import schedule
import time
import threading
import pytz
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
app.mount("/static", StaticFiles(directory="/app"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    with open("/app/index.html", "r") as f:
        content = f.read()
    return content

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.filename != "":
        upload_dir = os.path.join("/app", "uploaded_files")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        print(f"File uploaded: {file_path}")  # Debug print
    response = {
        "filename": file.filename
    }
    return JSONResponse(response)

@app.post("/generate")
async def generate(data: dict):
    try:
        filename = data["filename"]
        new_rent = float(data["new_rent"])
        previous_rent = data.get("previous_rent")
        application_date = datetime.strptime(data["application_date"], "%Y-%m-%d")
        free_text = data.get("free_text", "")
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d") if data.get("end_date") else None

        upload_dir = os.path.join("/app", "uploaded_files")
        template_path = os.path.join("/app", "template.docx")

        pdf_path = os.path.join(upload_dir, filename)
        print(f"Processing PDF: {pdf_path}")  # Debug print
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Uploaded file not found: {pdf_path}")

        signees, address, transaction_id, current_rent = extract_info_from_pdf(pdf_path)

        if previous_rent is not None:
            current_rent = str(int(float(previous_rent)))

        output_folder = os.path.join("/app", "output")
        os.makedirs(output_folder, exist_ok=True)
        output_file_name = f"Rent_Increase_{transaction_id}.docx"
        output_path = os.path.join(output_folder, output_file_name)

        service_fee = new_rent * 0.0495

        docx_output_path = create_new_rent_increase_docx(
            template_path, signees, application_date,
            current_rent, new_rent, service_fee, address, transaction_id,
            free_text, end_date, output_path
        )

        print(f"DOCX created: {docx_output_path}")  # Debug print
        print(f"DOCX file exists: {os.path.exists(docx_output_path)}")  # Verify file existence

        # Convert the generated DOCX to HTML
        with open(docx_output_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value

        # Generate PDF from HTML with explicit font configuration
        css = CSS(string='''
            @font-face {
                font-family: 'Times New Roman';
                src: url('/app/fonts/times.ttf') format('truetype');
            }
            body {
                font-family: 'Times New Roman', serif;
            }
        ''')
        
        pdf_output = BytesIO()
        HTML(string=html_content).write_pdf(pdf_output, stylesheets=[css])
        pdf_output.seek(0)

        # Save PDF file
        pdf_file_name = f"Rent_Increase_{transaction_id}.pdf"
        pdf_output_path = os.path.join(output_folder, pdf_file_name)
        with open(pdf_output_path, "wb") as pdf_file:
            pdf_file.write(pdf_output.getvalue())

        print(f"PDF created: {pdf_output_path}")  # Debug print
        print(f"PDF file exists: {os.path.exists(pdf_output_path)}")  # Verify file existence

        # Clean up the uploaded PDF file
        os.remove(pdf_path)
        print(f"Uploaded file removed: {pdf_path}")  # Debug print

        # Schedule file deletion after 5 minutes
        schedule_file_deletion(docx_output_path, 300)  # 300 seconds = 5 minutes
        schedule_file_deletion(pdf_output_path, 300)

        expiry_time = datetime.now() + timedelta(minutes=5)

        response = {
            "status": "success",
            "docx_path": f"/download/{output_file_name}",
            "pdf_path": f"/download/{pdf_file_name}",
            "html_preview": html_content,
            "expiry_time": expiry_time.isoformat(),
            "docx_filename": output_file_name,
            "pdf_filename": pdf_file_name
        }
        print(f"Response prepared: {response}")  # Debug print
        return JSONResponse(response)

    except Exception as e:
        import traceback
        error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will print to the console/logs
        raise HTTPException(status_code=500, detail=error_msg)

# Pydantic model for the new direct generation endpoint
class DirectGenerateRequest(BaseModel):
    signees: List[str]
    address: str
    transaction_id: Optional[str] = "N/A"
    current_rent: str # Keep as string to match potential PDF extraction format
    new_rent: float
    application_date: str # Expects YYYY-MM-DD
    percentage_fee: float
    free_text: Optional[str] = ""
    end_date: Optional[str] = None # Expects YYYY-MM-DD

@app.post("/generate_direct_pdf")
async def generate_direct_pdf(request_data: DirectGenerateRequest):
    try:
        application_date_dt = datetime.strptime(request_data.application_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(request_data.end_date, "%Y-%m-%d") if request_data.end_date else None

        template_path = os.path.join("/app", "template.docx")
        output_folder = os.path.join("/app", "output")
        os.makedirs(output_folder, exist_ok=True)
        
        # Use a timestamp or a more unique ID if transaction_id can be N/A frequently
        # For now, using transaction_id or a timestamp if it's N/A
        base_file_id = request_data.transaction_id if request_data.transaction_id and request_data.transaction_id != "N/A" else datetime.now().strftime("%Y%m%d%H%M%S")
        output_file_name_docx = f"Rent_Increase_{base_file_id}.docx"
        output_path_docx = os.path.join(output_folder, output_file_name_docx)

        service_fee = request_data.new_rent * request_data.percentage_fee

        docx_output_path = create_new_rent_increase_docx(
            template_path=template_path,
            signees=request_data.signees,
            application_date=application_date_dt,
            current_rent=str(request_data.current_rent), # Ensure it's a string as expected by create_new_rent_increase_docx
            new_rent=request_data.new_rent,
            service_fee=service_fee,
            address=request_data.address,
            transaction_id=request_data.transaction_id,
            free_text=request_data.free_text,
            end_date=end_date_dt,
            output_path=output_path_docx
        )

        print(f"DOCX created directly: {docx_output_path}")
        print(f"DOCX file exists: {os.path.exists(docx_output_path)}")

        with open(docx_output_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value

        css = CSS(string='''
            @font-face {
                font-family: 'Times New Roman';
                src: url('/app/fonts/times.ttf') format('truetype');
            }
            body {
                font-family: 'Times New Roman', serif;
            }
        ''')
        
        pdf_output_bytesio = BytesIO()
        HTML(string=html_content).write_pdf(pdf_output_bytesio, stylesheets=[css])
        pdf_output_bytesio.seek(0)

        output_file_name_pdf = f"Rent_Increase_{base_file_id}.pdf"
        output_path_pdf = os.path.join(output_folder, output_file_name_pdf)
        with open(output_path_pdf, "wb") as pdf_file:
            pdf_file.write(pdf_output_bytesio.getvalue())

        print(f"PDF created directly: {output_path_pdf}")
        print(f"PDF file exists: {os.path.exists(output_path_pdf)}")

        schedule_file_deletion(docx_output_path, 300) # 5 minutes
        schedule_file_deletion(output_path_pdf, 300)

        expiry_time = datetime.now() + timedelta(minutes=5)

        response = {
            "status": "success",
            "docx_path": f"/download/{output_file_name_docx}",
            "pdf_path": f"/download/{output_file_name_pdf}",
            "html_preview": html_content,
            "expiry_time": expiry_time.isoformat(),
            "docx_filename": output_file_name_docx,
            "pdf_filename": output_file_name_pdf
        }
        return JSONResponse(response)

    except Exception as e:
        import traceback
        error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/download/{filename}")
async def download(filename: str):
    output_folder = os.path.join("/app", "output")
    file_path = os.path.join(output_folder, filename)
    
    print(f"Attempting to download: {file_path}")  # Debug print
    print(f"File exists: {os.path.exists(file_path)}")  # Verify file existence
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debug print
        raise HTTPException(status_code=404, detail="File not found or has expired")
    
    if filename.endswith('.docx'):
        media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        file_type = 'docx'
    elif filename.endswith('.pdf'):
        media_type = 'application/pdf'
        file_type = 'pdf'
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    return FileResponse(file_path, media_type=media_type, filename=filename)


def delete_all_files():
    directories = ['/app/uploaded_files', '/app/output']
    for directory in directories:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_schedule():
    stockholm_tz = pytz.timezone('Europe/Stockholm')
    schedule.every().day.at("00:00").do(delete_all_files).timezone = stockholm_tz
    
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()

@app.on_event("startup")
async def startup_event():
    start_schedule()

if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")