import os # For file paths and reading environment variables
from dotenv import load_dotenv # To load variables from the .env file
import resend # The Resend email service library
import base64 # Used to encode the PDF as text for email

# Step 1: Load the variables from .env file
load_dotenv()

# Step 2: Get my Resend API key from the environment .env file
resend.api_key = os.environ["RESEND_API_KEY"]

# Step 3: Define the path to the PDF file to ensure that the PDF is found in the same folder as my script
pdf_path = os.path.join(os.path.dirname(__file__), "form.pdf")

# Step 4: Open the PDF in binary mode, read its contents, and encode it to base64

with open(pdf_path, "rb") as f:
    encoded_pdf = base64.b64encode(f.read()).decode()

# Step 5: Email recipient
recipient = [
    "nouranasir33@gmail.com",
]

# Step 6: Email content including the attachement
params = {
    "from": "Acme <onboarding@resend.dev>",
    "to": recipient,
    "subject": "Email Service Trial 2",
    "html": "<strong>Welcome to ARCH!</strong>",
    "attachments": [
        {
            "filename": "form.pdf",
            "content": encoded_pdf,
            "type": "application/pdf" 
        }
    ]
}

# Step 7: Send the email
try:
    response = resend.Emails.send(params)
    print("Email sent successfully.")
    print("Response:", response)
except Exception as e:
    print("Failed to send email.")
    print("Error:", e)
