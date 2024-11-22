import os
import zipfile

def create_eb_zip():
    # Save in current directory
    output_path = 'eb_app1.zip'
    
    files_to_zip = [
        'Dockerfile',
        'streamlit_requirements.txt',
        'streamlit_app/streamlit_app1.py',
        'src/',
        'models/',
        'data/'
    ]
    
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
    
    print(f"Created zip file: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_eb_zip()