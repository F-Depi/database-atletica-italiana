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

# Example usage
pdf_url = "https://www.fidal.it/upload/files/Statistiche/2004/Outdoor2004Msito.pdf"
save_as = "pdf-fidal/Outdoor2004Msito.pdf"
download_pdf(pdf_url, save_as)

