ALLOWED_EXTENSIONS = {"java", "py"}

def allowed_file(filename: str, project: str):
    if '.' in filename: 
        filename = filename.rsplit(".")
        return filename[0].lower() == project and filename[1] in ALLOWED_EXTENSIONS
    return False



