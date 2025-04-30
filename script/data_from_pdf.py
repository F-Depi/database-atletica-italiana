import fitz  # PyMuPDF
import re
import csv

def extract_results(pdf_path, output_csv):
    doc = fitz.open(pdf_path)
    all_elements = []

    for page in doc:
        text = page.get_text()
        elements = text.split('\n')
        all_elements.extend([element.strip() for element in elements])

    results = []
    result_line = []

    for element in all_elements:
        result_line.append(element)
        if re.search(r'\d{1,2}-\d{1,2}', element):  # End of a result line
            results.append(result_line)
            result_line = []

    # Write to CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for result in results:
            writer.writerow(result)

    print(f"Extracted {len(results)} results to {output_csv}")

# Example usage
amb = 'Outdoor'
for year in range(2001, 2005, 1):
    pdf_path = f"pdf-fidal/{amb}{year}.pdf"
    output_csv = f"data-pdf-fidal/{amb}{year}.csv"
    extract_results(pdf_path, output_csv)

