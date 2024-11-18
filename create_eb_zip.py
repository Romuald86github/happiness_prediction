import os
import zipfile
import shutil

def create_eb_zip():
    # Create temp zip in current directory
    temp_zip = 'eb_app.zip'
    desktop_path = '/Users/romualdchristialtcheutchoua/Desktop/eb_app.zip'
    
    files_to_zip = [
        'Dockerfile',
        'requirements.txt',
        'streamlit_app/',
        'src/',
        'models/'
    ]
    
    with zipfile.ZipFile(temp_zip, 'w') as zipf:
        for item in files_to_zip:
            if os.path.isfile(item):
                zipf.write(item)
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '.')
                        zipf.write(file_path, arcname)
    
    # Move zip to desktop
    shutil.move(temp_zip, desktop_path)
    print(f"Created zip file at: {desktop_path}")

if __name__ == "__main__":
    create_eb_zip()