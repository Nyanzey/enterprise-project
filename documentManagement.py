import os
import shutil
import json
import csv

def copy_to_local(src_folder, dst_folder):
    # Ensure the destination folder exists
    os.makedirs(dst_folder, exist_ok=True)
    
    # Loop through the files in the source folder
    for filename in os.listdir(src_folder):
        src_file = os.path.join(src_folder, filename)
        # Check if it is a file (not a directory)
        if os.path.isfile(src_file):
            # Copy the file to the destination folder
            shutil.copy(src_file, dst_folder)
            print(f'Copied: {filename}')

def get_file_info(file_path):
    # Get the base name of the file (filename with extension)
    filename_with_extension = os.path.basename(file_path)
    # Split the filename into name and extension
    name, extension = os.path.splitext(filename_with_extension)
    return name, extension

def output_metadata(source_path, dest_path, doc_type, keywords, similarity_scores):
    output_data = {
        "document_path": source_path,
        "type": doc_type,
        "keywords": keywords,
        "similarity_scores": similarity_scores
    }
    source_name, source_ext = get_file_info(source_path)
    dest_name, dest_ext = get_file_info(dest_path)
    print(dest_ext)

    if dest_ext == '.csv':
        # Write or append to CSV file
        file_exists = False
        try:
            with open(dest_path, mode='r') as f:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(dest_path, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=output_data.keys())
            # Write headers only once
            if not file_exists:
                writer.writeheader()
            writer.writerow(output_data)

    elif dest_ext == '.json':
        for key, val in output_data['similarity_scores'].items():
            output_data['similarity_scores'][key] = str(val)
        # Write or append to JSON file
        try:
            with open(dest_path, 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data.append(output_data)

        with open(dest_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    else:
        raise ValueError("Invalid format specified. Use 'csv' or 'json'.")

    print(f"Metadata for '{source_name}' saved successfully in {dest_path}")


def upload_to_web(src_folder, web_media_folder):
    # to do ....
    pass

def copy_to_remote(src_folder, remote_addr):
    # to do ....
    pass
