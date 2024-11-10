import documentAnalysis as danalysis
import documentConvert as dconvert
import documentManagement as dmanage
import os

# Local back up folder
BACKUP_DIR = None

# Remote back up folder
REMOTE_BACKUP_ADDR = 'backup/'

# Input directory
IN_DIR = './input'

# Output directory
OUT_DIR =  './output'

# Web media directory
WEB_DIR = None

# Metadata directory
META_DIR = './meta'

# Convert to searchable
def convert_files():
    # Loop through the files in the input directory
    for filename in os.listdir(IN_DIR):
        # Create the full path to the file
        full_path = os.path.join(IN_DIR, filename)

        # Check if it is a file (not a directory)
        if os.path.isfile(full_path):
            name, _ = os.path.splitext(filename)
            
            print(f'converting {IN_DIR}/{filename} .....')
            dconvert.convert_to_searchable_pdf(f'{IN_DIR}/{filename}', f'{OUT_DIR}/{name}-searchable.pdf')
            print('done')

# Document analysis
def extract_meta(meta_format = '.json'):
    for filename in os.listdir(OUT_DIR):
        # Create the full path to the file
        full_path = os.path.join(OUT_DIR, filename)

        # Check if it is a file (not a directory)
        if os.path.isfile(full_path):
            name, _ = os.path.splitext(filename)
            dest_path = os.path.join(META_DIR, name+meta_format)
            type, kwords, scores = danalysis.analyze_pdf_document(full_path)
            dmanage.output_metadata(full_path, dest_path, type, kwords, scores)

def backup():
    # Upload to website (should put the output in paperless media folder)
    if WEB_DIR:
        dmanage.upload_to_web(OUT_DIR, WEB_DIR)

    # Back up to local dir
    if BACKUP_DIR:
        dmanage.copy_to_local(OUT_DIR, BACKUP_DIR)

    # Back up to remote addr (maybe like s3)
    if REMOTE_BACKUP_ADDR:
        dmanage.copy_to_remote(OUT_DIR, REMOTE_BACKUP_ADDR)

convert_files()
backup()
extract_meta()
