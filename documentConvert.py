import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os

def convert_image_to_searchable_pdf(image_path, output_path):
    pdf_data = pytesseract.image_to_pdf_or_hocr(image_path, extension='pdf')
    with open(output_path, 'wb') as f:
        f.write(pdf_data)

def convert_pdf_to_searchable_pdf(pdf_path, output_path):
    # Convert each page in the PDF to an image
    images = convert_from_path(pdf_path)

    # Temporary storage for each page's searchable PDF
    temp_pdfs = []

    # Convert each image to a searchable PDF page
    for i, image in enumerate(images):
        temp_pdf = f"temp_page_{i}.pdf"
        pdf_data = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
        with open(temp_pdf, 'wb') as f:
            f.write(pdf_data)
        temp_pdfs.append(temp_pdf)

    # Merge all the individual page PDFs into a single searchable PDF
    pdf_writer = PdfWriter()
    for temp_pdf in temp_pdfs:
        with open(temp_pdf, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

    # Write the merged PDF to output
    with open(output_path, 'wb') as f:
        pdf_writer.write(f)

    # Clean up temporary files
    for temp_pdf in temp_pdfs:
        os.remove(temp_pdf)

def convert_to_searchable_pdf(input_path, output_path):
    if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        # Input is an image
        convert_image_to_searchable_pdf(input_path, output_path)
    elif input_path.lower().endswith('.pdf'):
        # Input is a PDF
        convert_pdf_to_searchable_pdf(input_path, output_path)
    else:
        raise ValueError("Unsupported file type. Please provide an image or PDF.")