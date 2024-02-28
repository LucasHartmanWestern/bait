if __name__ == '__main__':
    print("Running Billing Parser")

import pdfplumber

# Path to the PDF file
pdf_path = r'C:\Users\epigo\Documents\bait\billing parser\01-20-2024.pdf'

# Open the PDF file
with pdfplumber.open(pdf_path) as pdf:

    # Loop through each page
    for page in pdf.pages:
        # Extract text from the page
        text = page.extract_text()
        print("Text extracted from the page:", text)

        # Check for tables and extract them
        tables = page.extract_tables()
        for table in tables:
            # Do something with the table data
            print("Table found on the page:", table)
