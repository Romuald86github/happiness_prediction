import os
import zipfile

def create_eb_zip():
    # Set output path
    output_path = '/Users/romualdchristialtcheutchoua/Desktop/eb_app.zip'
    
    # Files/directories to include
    files_to_zip = [
        'Dockerfile',
        'streamlit_requirements.txt',
        'streamlit_app/',
        'src/',
        'models/'
    ]
    
    # Create zip file
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for item in files_to_zip:
            if os.path.isfile(item):
                zipf.write(item)
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '.')
                        zipf.write(file_path, arcname)

if __name__ == "__main__":
    create_eb_zip()