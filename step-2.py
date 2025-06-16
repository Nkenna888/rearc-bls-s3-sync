import requests
import boto3
import logging
import os

# Config
DATAUSA_URL = "https://rearc-bls-nahom.s3.amazonaws.com/datausa/population.json"
S3_BUCKET = "rearc-bls-nahom"  # Replace with your bucket
S3_KEY = "datausa/population.json"

# Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# S3 Upload
def upload_population_json():
    try:
        logging.info("Downloading population.json from DataUSA...")
        response = requests.get(DATAUSA_URL)
        response.raise_for_status()
        content = response.content

        logging.info("Uploading to S3...")
        s3 = boto3.client('s3')
        s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=content)
        logging.info("Upload successful: population.json")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    upload_population_json()
