import re
import pdfplumber
from docx import Document
from datetime import datetime
import os
import threading
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("No GROQ_API_KEY environment variable has been set.")


client = Groq(
    api_key=GROQ_API_KEY
)

def translate_text(text):
    if not text:  # Skip translation if text is empty
        return ""
    
    prompt = f"""Translate the following Swedish text to English, do not add any commentary to the translation:
    {text}
    Translation:"""
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
        temperature=0.1,
        max_tokens=200,
        top_p=1,
    )
    
    response = chat_completion.choices[0].message.content.strip()
    
    # Extract only the translated text
    translation_start = response.find('"') + 1
    translation_end = response.rfind('"')
    if translation_start > 0 and translation_end > translation_start:
        return response[translation_start:translation_end]
    else:
        return response  # Return full response if we can't extract the translation

def schedule_file_deletion(file_path, delay_seconds):
    def delete_file():
        print(f"Attempting to delete file: {file_path}")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found for deletion: {file_path}")

    print(f"Scheduling deletion of {file_path} in {delay_seconds} seconds")
    threading.Timer(delay_seconds, delete_file).start()

def extract_info_from_pdf(pdf_path):
    print(f"Extracting info from PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print(f"Extracted text: {text}")

        landlord_name = re.search(r'\(1\)(.*?),', text).group(1).strip()
        tenant_name = re.search(r'\(2\)(.*?)(,|\()', text).group(1).strip()
        address = re.search(r'adress\s+(.*?),', text, re.IGNORECASE).group(1).strip()
        transaction_search = re.search(r'Transaktion\s+(\S+)', text)
        transaction_id = transaction_search.group(1).strip() if transaction_search else "N/A"

        current_rent = None
        for page in pdf.pages:
            text = page.extract_text()
            match = re.search(r'Hyran är\s+([\d\s]+)', text)
            if match:
                current_rent = match.group(1).strip().replace(" ", "")
                break

        if current_rent is None:
            raise ValueError("Current rent not found in the PDF")

        print(f"Extracted info: {landlord_name}, {tenant_name}, {address}, {transaction_id}, {current_rent}")
        return landlord_name, tenant_name, address, transaction_id, current_rent

def replace_placeholders(doc, placeholders):
    def process_paragraph(paragraph):
        text = paragraph.text
        
        for key, value in placeholders.items():
            text = text.replace(key, str(value))
        
        paragraph.clear()
        
        is_bold_line = ("(1)" in text and "Hyresvärden" in text) or \
                       ("(2)" in text and "Hyresgästen" in text) or \
                       ("(1)" in text and "Landlord" in text) or \
                       ("(2)" in text and "Tenant" in text) or \
                       text.strip() == "Landlord" or \
                       text.strip() == "Tenant" or \
                       text.strip().startswith("_____")
        
        run = paragraph.add_run(text)
        run.bold = is_bold_line

    for paragraph in doc.paragraphs:
        process_paragraph(paragraph)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    process_paragraph(paragraph)

def set_font_to_times_new_roman(doc):
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = 'Times New Roman'
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = 'Times New Roman'

def create_new_rent_increase_docx(template_path, landlord_name, tenant_name, application_date, current_rent, new_rent, service_fee, address, transaction_id, free_text, end_date, output_path):
    print(f"Creating new rent increase DOCX: {output_path}")
    doc = Document(template_path)

    rounded_service_fee = round(service_fee)

    if end_date:
        when_se = f"till och med {end_date.strftime('%Y-%m-%d')}. Därefter återgår hyran till föregående belopp"
        when_en = f"{end_date.strftime('%Y-%m-%d')}. After which the rent returns to the previous amount"
    else:
        when_se = "tillsvidare"
        when_en = "further notice"

    # Translate free_text to English only if it's not empty
    print(f"Original free_text: {free_text}")  # Debug log
    free_text_en = translate_text(free_text) if free_text else ''
    print(f"Translated free_text: {free_text_en}")  # Debug log

    placeholders = {
        '[LANDLORD_NAME]': landlord_name,
        '[TENANT_NAME]': tenant_name,
        '[ADDRESS]': address,
        '[TRANSACTION_ID]': transaction_id,
        '[CURRENT_RENT]': current_rent,
        '[NEW_RENT]': f"{new_rent:.0f}",
        '[SERVICE_FEE]': str(rounded_service_fee),
        '[APPLICATION_DATE]': application_date.strftime('%Y-%m-%d'),
        '[TODAYS_DATE]': datetime.today().strftime('%Y-%m-%d'),
        '[FREE_TEXT]': free_text,
        '[FREE_TEXT_EN]': free_text_en,
        '[WHEN_SE]': when_se,
        '[WHEN_EN]': when_en,
    }

    print("Placeholders to be replaced:", placeholders)

    replace_placeholders(doc, placeholders)

    set_font_to_times_new_roman(doc)

    doc.save(output_path)
    print(f"DOCX saved: {output_path}")

    return output_path