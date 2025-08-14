import os
from typing import List, Dict

def start_signing_process(file_path: str, title: str, signees: List[Dict]) -> Dict:
    """
    This is a placeholder function to simulate starting a signing process with Scrive.
    In a real implementation, this function would contain the logic to call the Scrive API.

    Args:
        file_path (str): The absolute path to the document to be signed.
        title (str): The title of the document in the Scrive process.
        signees (List[Dict]): A list of signee information.

    Returns:
        Dict: A mock response from the Scrive API.
    """
    print("--- SIMULATING SEND TO SCRIVE ---")
    print(f"File to send: {file_path}")
    print(f"Document Title: {title}")
    print("Signees:")
    for i, signee in enumerate(signees):
        print(f"  - Signee {i+1}:")
        print(f"    Name: {signee.get('name')}")
        print(f"    Email: {signee.get('email')}")
        print(f"    Phone: {signee.get('phone_number')}")
        print(f"    Requires Swedish BankID: {signee.get('has_swedish_id')}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document to be signed not found at: {file_path}")

    # Here you would add your actual Scrive API call
    # For example:
    # scrive_client = Scrive(client_id='YOUR_ID', client_secret='YOUR_SECRET')
    # document = scrive_client.create_document_from_file(file_path)
    # ... add parties, set options, and start the document ...
    
    print("--- SIMULATION COMPLETE ---")
    
    # Return a mock success response
    return {
        "status": "success",
        "message": "Document successfully sent to Scrive (simulation).",
        "scrive_document_id": "mock-scrive-document-id-1234567890"
    }
