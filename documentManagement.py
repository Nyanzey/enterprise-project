import os
import shutil
import json
import csv
import boto3
import logging
from botocore.exceptions import ClientError
import requests
from bs4 import BeautifulSoup

AWS_S3_BUCKET_NAME = 'docmanager-backup'
AWS_REGION = 'us-east-1'
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None

with open('./awsKey.txt', 'r') as f:
    AWS_ACCESS_KEY = f.read()

with open('./awsSecretKey.txt', 'r') as f:
    AWS_SECRET_KEY = f.read()

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


def upload_to_web(src_folder):
    # Start a session
    session = requests.Session()
    
    # Step 1: Get the login page to retrieve the CSRF token
    login_page_url = "http://127.0.0.1:8000/accounts/login/?next=/"
    login_page_response = session.get(login_page_url)
    
    if login_page_response.status_code != 200:
        print("Failed to load login page.")
        return

    # Parse the HTML to find the CSRF token
    soup = BeautifulSoup(login_page_response.text, 'html.parser')
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

    # Step 2: Prepare login data with the CSRF token
    login_data = {
        "csrfmiddlewaretoken": csrf_token,
        "login": "admin",  # replace with actual username
        "password": "admin"  # replace with actual password
    }

    # Set headers as per the request structure
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": login_page_url,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://127.0.0.1:8000",
        "Upgrade-Insecure-Requests": "1",
    }

    # Step 3: Send the login POST request
    login_response = session.post(login_page_url, data=login_data, headers=headers)
    if login_response.status_code == 200 and "sessionid" in session.cookies:
        print("Login successful.")

        # Set headers for file upload
        post_url = "http://127.0.0.1:8000/api/documents/post_document/"
        headers["X-CSRFToken"] = session.cookies.get("csrftoken")
        headers["Accept"] = "application/json; version=5"
        headers.pop("Content-Type", None)  # Remove Content-Type for multipart/form-data

        # Step 4: Upload each file in the folder
        for filename in os.listdir(src_folder):
            file_path = os.path.join(src_folder, filename)
            if os.path.isfile(file_path):  # Ensure it's a file
                with open(file_path, "rb") as file:
                    files = {"document": (filename, file)}
                    response = session.post(post_url, headers=headers, files=files)
                    print(f"Uploaded {filename}: Status Code {response.status_code}")
                    if response.status_code == 200:
                        print("Response:", response.json())
                    else:
                        print(f"Failed to upload {filename}")
    else:
        print("Login failed with status code:", login_response.status_code)


def copy_to_remote(src_folder, remote_folder):
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    for root, dirs, files in os.walk(src_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            # Construct the remote file path in S3
            remote_file_path = os.path.join(remote_folder, file)
            print(local_file_path,' -> ', remote_file_path)
            sup = input('Upload ? [y/n]: ')
            if sup != 'y':
                continue
            try:
                response = s3_client.upload_file(local_file_path, AWS_S3_BUCKET_NAME, remote_file_path)
            except ClientError as e:
                logging.error(f"Error uploading {local_file_path}: {e}")
                return False
            
    print('Files uploaded to remote backup successfully')
    return True
