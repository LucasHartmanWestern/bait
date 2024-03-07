if __name__ == '__main__':
    print("Running Billing Parser")

import pdfplumber

# Path to the PDF file
pdf_path = r'C:\Users\epigo\Documents\bait\billing parser\01-20-2024.pdf'

# Open the PDF file
with pdfplumber.open(pdf_path) as pdf:
    # Loop through each page, using enumerate to get the page number (starting from 1)
    for i, page in enumerate(pdf.pages, start=1):
        print("--------------------------------------------------------")
        print(f"Page {i} Information:")
        print("--------------------------------------------------------")
        # For the first two pages, extract and display only tables
        if i <= 2:
            tables = page.extract_tables()
            for table in tables:
                print(f"Table found on page {i}:", table)
        # For the remaining pages, extract and display only text
        else:
            # Extract text from the page
            text = page.extract_text()
            if text:  # Check if there's any text extracted to avoid printing None
                print(f"Text extracted from page {i}:", text)
