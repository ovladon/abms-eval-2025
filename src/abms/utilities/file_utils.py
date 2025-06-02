# file_utils.py
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png', 'mp3', 'wav', 'mp4', 'avi', 'csv', 'xlsx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_and_save_file(file, upload_folder: str) -> str:
    if file and allowed_file(file.name):
        filename = secure_filename(file.name)
        file_path = os.path.join(upload_folder, filename)
        with open(file_path, "wb") as f:
            f.write(file.read())
        return file_path
    else:
        raise ValueError("File type not allowed.")

