# shared/utilities.py

import os
import re
import chardet
import mimetypes
import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text
from PIL import Image
import pytesseract
import pypandoc

class FileHandler:
    def __init__(self):
        pass

    def detect_file_type(self, file_name):
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type:
            return mime_type
        else:
            # Fallback to file extension
            ext = os.path.splitext(file_name)[1].lower()
            return ext

    def read_file(self, file_path):
        file_type = self.detect_file_type(file_path)
        if file_type in ['text/plain', '.txt', 'txt']:
            return self.read_txt_file(file_path)
        elif file_type in ['application/pdf', '.pdf', 'pdf']:
            return self.read_pdf_file(file_path)
        elif file_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.doc', '.docx', 'doc', 'docx']:
            return self.read_doc_file(file_path)
        elif file_type in ['application/rtf', '.rtf', 'rtf']:
            return self.read_rtf_file(file_path)
        elif file_type.startswith('image/') or file_type in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            return self.read_image_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def read_txt_file(self, file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
            text = raw_data.decode(encoding)
        return text

    def read_pdf_file(self, file_path):
        text = extract_pdf_text(file_path)
        return text

    def read_doc_file(self, file_path):
        text = docx2txt.process(file_path)
        return text

    def read_rtf_file(self, file_path):
        # Use pypandoc to convert RTF to plain text
        text = pypandoc.convert_file(file_path, 'plain')
        return text

    def read_image_file(self, file_path):
        # Use OCR to extract text from images
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text

    def preprocess_text(self, text):
        # Basic preprocessing: remove extra whitespace, non-printable characters, etc.
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

