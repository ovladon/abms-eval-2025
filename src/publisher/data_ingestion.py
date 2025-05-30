# publisher/data_ingestion.py

import streamlit as st
import chardet
import mimetypes
import pdfminer.high_level
import docx2txt
import pytesseract
from PIL import Image

class DataIngestion:
    def get_text(self):
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx", "jpg", "jpeg", "png", "mp3", "wav", "mp4", "avi", "csv", "xlsx"])

        if uploaded_file is not None:
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            if mime_type == 'text/plain':
                raw_text = uploaded_file.read()
                encoding = chardet.detect(raw_text)['encoding']
                text = raw_text.decode(encoding)
                return text
            elif mime_type == 'application/pdf':
                text = pdfminer.high_level.extract_text(uploaded_file)
                return text
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                text = docx2txt.process(uploaded_file)
                return text
            elif mime_type in ['image/png', 'image/jpeg']:
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image)
                return text
            else:
                st.write("Unsupported file type.")
                return None
        else:
            text_input = st.text_area("Or enter text here:")
            if text_input:
                return text_input
            else:
                return None

