import requests
import boto3
import os

BUCKET_NAME = os.environ.get("BUCKET_NAME", "rearc-bls-nahom")
KEY_NAME = "datausa/population.json"
API_URL = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"

def main():
    print("🔄 Fetching data from DataUSA API...")
    response = requests.get(API_URL)
    response.raise_for_status()

    s3 = boto3.client("s3")
    print(f"⬆️ Uploading to s3://{BUCKET_NAME}/{KEY_NAME}")
    s3.put_object(Bucket=BUCKET_NAME, Key=KEY_NAME, Body=response.content)

    print("✅ Done.")

if __name__ == "__main__":
    main()
