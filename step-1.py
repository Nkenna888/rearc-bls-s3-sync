import os
import requests
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import logging

# --- Configuration ---
SOURCE_URL = 'https://download.bls.gov/pub/time.series/pr/'
USER_AGENT = 'Your Name (nahomkenna14@outlook.com)'  # Replace with your info
S3_BUCKET = 'rearc-bls-nahom'                   # Replace with your bucket name
S3_PREFIX = 'bls-time-series/'

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --- AWS S3 Client ---
s3 = boto3.client('s3')

def list_s3_files():
    """List files currently in the S3 target prefix"""
    paginator = s3.get_paginator('list_objects_v2')
    keys = set()
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX):
        for obj in page.get('Contents', []):
            key = obj['Key'].replace(S3_PREFIX, '')
            keys.add(key)
    return keys

def get_remote_file_list():
    """Scrape the list of files from the BLS directory page"""
    headers = {'User-Agent': USER_AGENT}
    try:
        resp = requests.get(SOURCE_URL, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch BLS page: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    return [
        a['href'] for a in soup.find_all('a', href=True)
        if a['href'].endswith(('.txt', '.dat'))
    ]

def download_file(file_name):
    """Download file content from BLS"""
    headers = {'User-Agent': USER_AGENT}
    file_url = urljoin(SOURCE_URL, file_name)
    try:
        resp = requests.get(file_url, headers=headers)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.RequestException as e:
        logging.warning(f"Failed to download {file_name}: {e}")
        return None

def upload_to_s3(file_name, content):
    """Upload file to S3 under the given prefix"""
    s3_key = os.path.join(S3_PREFIX, os.path.basename(file_name))  # CLEAN S3 KEY
    try:
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=content)
        logging.info(f"Uploaded: {os.path.basename(file_name)}")
    except ClientError as e:
        logging.error(f"Upload failed for {file_name}: {e}")

def delete_from_s3(file_name):
    """Delete a file from S3 if it's no longer in the source"""
    s3_key = os.path.join(S3_PREFIX, file_name)
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        logging.info(f"Deleted: {file_name}")
    except ClientError as e:
        logging.error(f"Delete failed for {file_name}: {e}")

def sync():
    logging.info("Starting sync process...")
    remote_files = set(get_remote_file_list())
    s3_files = list_s3_files()

    to_upload = remote_files - s3_files
    to_delete = s3_files - remote_files

    logging.info(f"Remote files: {len(remote_files)} | S3 files: {len(s3_files)}")
    logging.info(f"Uploading {len(to_upload)} new files...")
    logging.info(f"Deleting {len(to_delete)} stale files...")

    for file_name in sorted(to_upload):
        content = download_file(file_name)
        if content:
            upload_to_s3(file_name, content)

    for file_name in sorted(to_delete):
        delete_from_s3(file_name)

    logging.info("Sync completed successfully.")

if __name__ == '__main__':
    sync()
