import re
import pdfplumber
from docx import Document
from datetime import datetime
import os
import threading

def schedule_file_deletion(file_path, delay_seconds):
    def delete_file():
        print(f"Attempting to delete file: {file_path}")  # Debug print
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found for deletion: {file_path}")

    print(f"Scheduling deletion of {file_path} in {delay_seconds} seconds")  # Debug print
    threading.Timer(delay_seconds, delete_file).start()

def extract_info_from_pdf(pdf_path):
    print(f"Extracting info from PDF: {pdf_path}")  # Debug print
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print(f"Extracted text: {text}")  # Debug print

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
                current_rent = match.group(1).strip().replace(" ", "")  # Remove spaces
                break

        if current_rent is None:
            raise ValueError("Current rent not found in the PDF")

        print(f"Extracted info: {landlord_name}, {tenant_name}, {address}, {transaction_id}, {current_rent}")  # Debug print
        return landlord_name, tenant_name, address, transaction_id, current_rent

def replace_placeholders(doc, placeholders):
    def process_paragraph(paragraph):
        text = paragraph.text
        
        # Replace all placeholders
        for key, value in placeholders.items():
            text = text.replace(key, str(value))
        
        # Clear the paragraph
        paragraph.clear()
        
        # Check if this is a line that should be bold
        is_bold_line = ("(1)" in text and "Hyresvärden" in text) or \
                       ("(2)" in text and "Hyresgästen" in text) or \
                       ("(1)" in text and "Landlord" in text) or \
                       ("(2)" in text and "Tenant" in text) or \
                       text.strip() == "Landlord" or \
                       text.strip() == "Tenant" or \
                       text.strip().startswith("_____")
        
        # Add the text back with appropriate formatting
        run = paragraph.add_run(text)
        run.bold = is_bold_line

    # Process main document body
    for paragraph in doc.paragraphs:
        process_paragraph(paragraph)

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    process_paragraph(paragraph)

def set_font_to_times_new_roman(doc):
    # Set the default font for the document
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    
    # Iterate through all paragraphs and runs to set the font
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = 'Times New Roman'
    
    # Iterate through all tables, cells, paragraphs, and runs to set the font
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = 'Times New Roman'

def create_new_rent_increase_docx(template_path, landlord_name, tenant_name, application_date, current_rent, new_rent, service_fee, address, transaction_id, free_text, end_date, output_path):
    print(f"Creating new rent increase DOCX: {output_path}")  # Debug print
    doc = Document(template_path)

    rounded_service_fee = round(service_fee)

    when_se = end_date.strftime('%Y-%m-%d') if end_date else "tillsvidare"
    when_en = end_date.strftime('%Y-%m-%d') if end_date else "further notice"

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
        '[FREE_TEXT]': free_text if free_text else '',
        '[WHEN_SE]': when_se,
        '[WHEN_EN]': when_en,
    }

    print("Placeholders to be replaced:", placeholders)  # Debug print

    replace_placeholders(doc, placeholders)

    # Set the font to Times New Roman
    set_font_to_times_new_roman(doc)

    # Save as DOCX
    doc.save(output_path)
    print(f"DOCX saved: {output_path}")  # Debug print

    return output_path