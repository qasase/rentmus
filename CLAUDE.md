# Rentmus - Rent Change Application

## Project Overview
This is a FastAPI-based web application for generating rental contract modification documents. The application processes uploaded PDF rental contracts, extracts tenant information, and creates new rent increase documents in DOCX and PDF formats.

## Core Functionality
- **PDF Processing**: Extracts signee names, addresses, transaction IDs, and current rent from uploaded rental contracts
- **Document Generation**: Creates rent increase documents using a Word template with dynamic placeholder replacement
- **Multi-format Output**: Generates both DOCX and PDF versions of documents
- **Translation**: Translates Swedish text to English using DeepL API
- **Scrive Integration**: Placeholder integration for document signing via Scrive API
- **File Management**: Automatic cleanup of generated files after 5 minutes

## Key Files
- `app.py` - Main FastAPI application with REST endpoints
- `rent_utils.py` - Core utilities for PDF processing and document generation
- `scrive_utils.py` - Placeholder functions for Scrive API integration
- `template.docx` - Word template for rent increase documents
- `index.html` - Frontend web interface

## Environment Variables
- `DEEPL_API_KEY` - Required for text translation functionality (Swedish to English)
- `PORT` - Server port (defaults to 8000)

## Docker Configuration
The application runs in Docker with:
- Python 3.11 slim base image
- WeasyPrint dependencies for PDF generation
- Times New Roman font support
- Exposed on port 8000

## Development Commands

### Run the application
```bash
# Local development
uvicorn app:app --reload

# Docker
docker compose up
```

### Testing
Look for test commands in the README or package.json. No specific test framework detected in current files.

### Code Quality
- Always run linting and type checking after making changes
- Check if `ruff`, `black`, `mypy`, or similar tools are configured
- Ensure proper error handling and validation

## Important Notes
- Files are automatically deleted after 5 minutes for security
- Swedish text is translated to English for bilingual documents  
- PDF extraction uses regex patterns specific to Swedish rental contracts
- The application expects specific PDF formats with signee patterns like "(1) Name, (2) Another Name"

## API Endpoints
- `POST /upload` - Upload PDF rental contract
- `POST /generate` - Generate rent increase documents from uploaded PDF
- `POST /generate_direct_pdf` - Generate documents with manual input (no PDF upload)
- `POST /send_to_scrive` - Send documents for digital signing (placeholder)
- `GET /download/{filename}` - Download generated documents

## Security Considerations
- Uploaded files are cleaned up automatically
- All file paths are validated before processing
- CORS is enabled for all origins (consider restricting in production)
- No authentication implemented - consider adding for production use