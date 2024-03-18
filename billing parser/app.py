import os

import pdfplumber
if __name__ == '__main__':
    print("Running Billing Parser")
# Path to the PDF file
pdf_paths = [r'billing parser/Current_User.pdf',
             r'billing parser/Current_User1.pdf',
             r'billing parser/Current_User2.pdf',
             r'billing parser/Current_User3.pdf',
             r'billing parser/Current_User4.pdf']


# Function to process each PDF
def return_bills():
    result = ""
    for pdf_path in pdf_paths: # Iterate over each path
        with pdfplumber.open(pdf_path) as pdf:  # Open each PDF
            # Extract customer name from the file path
            customer_name = os.path.basename(pdf_path).replace('.pdf', '')  # Remove the .pdf extension

            # Loop through each page, using enumerate to get the page number (starting from 1)
            for i, page in enumerate(pdf.pages, start=1):
                result += "--------------------------------------------------------\n"
                result += f"Page {i} Information for {customer_name}:\n"  # Show the customer name instead of file path
                result += "--------------------------------------------------------\n"
                # For the first two pages, extract and display only tables
                if i <= 2:
                    tables = page.extract_tables()
                    for table in tables:
                        result += f"Table found on page {i}: {table}\n"
                # For the remaining pages, extract and display only text
                else:
                    # Extract text from the page
                    text = page.extract_text()
                    if text:  # Check if there's any text extracted to avoid printing None
                        result += f"Text extracted from page {i}: {text}\n"
    return result
