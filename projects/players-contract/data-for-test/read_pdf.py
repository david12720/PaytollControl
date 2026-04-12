import pdfplumber
from pathlib import Path
from bidi.algorithm import get_display

# 1. Define the file path using pathlib 
# pathlib handles Unicode paths and OS-specific slashes perfectly
file_name = "אביב גבלי חוזה בקרה 25-26.pdf"
file_path = Path(file_name)

# 2. Check if the file actually exists to avoid crashing
if not file_path.is_file():
    print(f"Error: The file '{file_name}' was not found in the current directory.")
else:
    # 3. Open the PDF file
    with pdfplumber.open(file_path) as pdf:
        
        # Loop through all the pages in the PDF
        for page_number, page in enumerate(pdf.pages):
            
            # Extract the raw text from the page
            raw_text = page.extract_text()
            
            if raw_text:
                # 4. Fix Right-To-Left (RTL) reading order
                # PDFs often store Hebrew left-to-right, making it read backwards.
                # get_display() flips the characters back to their proper reading order.
                readable_hebrew_text = get_display(raw_text)
                
                print(f"--- Page {page_number + 1} ---")
                print(readable_hebrew_text)
            else:
                print(f"--- Page {page_number + 1} ---")
                print("(No text found on this page)")