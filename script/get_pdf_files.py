import requests

def download_pdf(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        if 'application/pdf' in response.headers.get('Content-Type', ''):
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"PDF downloaded successfully as '{filename}'.")
        else:
            print("The URL does not point to a PDF file.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")

# Da 2002 a 2004
for year in range(2002, 2005, 1):
    pdf_url = f"https://www.fidal.it/upload/files/Statistiche/{year}/Outdoor{year}Msito.pdf"
    filename = f"pdf-fidal/Outdoor{year}.pdf"
    download_pdf(pdf_url, filename)
    pdf_url = f"https://www.fidal.it/upload/files/Statistiche/{year}/Indoor{year}Msito.pdf"
    filename = f"pdf-fidal/Indoor{year}.pdf"
    download_pdf(pdf_url, filename)

# 2001 è speciale ovviamente...
year = 2001
pdf_url = "https://www.fidal.it/upload/files/Statistiche/2001/ass2001Msito.pdf"
filename = f"pdf-fidal/Outdoor{year}.pdf"
download_pdf(pdf_url, filename)


