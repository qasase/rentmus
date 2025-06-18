
# Rent Change Application

## Overview

This project is a web-based application designed to facilitate the generation of rental contract modification documents. The application allows users to upload existing rental contracts in PDF format, specify new rent details, and generate updated rental agreements. The generated documents can be previewed and downloaded.

## Features

- Upload rental contracts in PDF format.
- Input new rent amount, application date, end date, and additional comments.
- Generate rental agreement modification documents in DOCX format.
- Preview the generated document.
- Download the generated document.

## Requirements

To run this project, you need to have the following dependencies installed:

- fastapi==0.70.0
- uvicorn==0.15.0
- gunicorn==20.1.0
- httpx==0.22.0
- pdfplumber==0.5.28
- python-docx
- pytz==2021.3
- python-multipart
- reportlab>=3.6.12
- docx2pdf==0.1.8
- mammoth==1.4.19

Install the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Project Structure

- `app.py`: The main FastAPI application file.
- `rent_utils.py`: Utility functions for processing rental contracts and generating documents.
- `index.html`: The frontend HTML file for the web application.
- `template.docx`: The DOCX template used for generating the modified rental agreements.
- `requirements.txt`: The list of dependencies required for the project.

## Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/rasmusdriving/render_rentmus_server.git
   cd rent-change-application
   ```

2. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   uvicorn app:app --reload
   ```

4. **Access the application:**

   Open your web browser and navigate to `http://127.0.0.1:8000`.

5. **Upload a PDF contract:**

   - Click on the "Upload a file" button or drag and drop a PDF file into the upload area.

6. **Input new rent details:**

   - Fill in the new rent amount, application date, optional end date, and any additional comments.

7. **Generate the document:**

   - Click on the "Generate Rent Change Document" button.
   - Preview the generated document.
   - Download the generated DOCX file.

## Running with Docker Compose

Alternatively, you can run the application using Docker Compose. This is the recommended method for development and deployment as it handles dependencies and environment setup within a container.

1.  **Ensure Docker and Docker Compose are installed.**

2.  **Build the Docker image (if not already built or if Dockerfile/requirements.txt changed):**

    ```bash
    docker compose build
    ```

3.  **Start the application:**

    ```bash
    docker compose up
    ```

    The application will be accessible at `http://localhost:8000`.

4.  **To stop the application:**

    Press `Ctrl+C` in the terminal where `docker compose up` is running, or run the following command from another terminal in the project root:

    ```bash
    docker compose down
    ```

## Endpoints

The application exposes the following endpoints:

- `POST /upload`: Upload a PDF file.
- `POST /generate`: Generate a modified rental agreement.

## Contributing

Feel free to contribute to this project by submitting a pull request. Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Mammoth](https://github.com/mwilliamson/mammoth)
- [ReportLab](https://www.reportlab.com/)

## Contact

For any inquiries or issues, please contact [your email address].

```

Make sure to replace placeholders like `https://github.com/yourusername/rent-change-application.git` and `[your email address]` with the appropriate information for your project.