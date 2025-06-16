import boto3, requests, os

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']
USER_AGENT = "Nahom Kenna (nahomkenna14@outlook.com)"

def lambda_handler(event, context):
    # Download BLS .txt file
    bls_url = "https://download.bls.gov/pub/time.series/pr/pr.txt"
    r = requests.get(bls_url, headers={"User-Agent": USER_AGENT})
    s3.put_object(Bucket=BUCKET, Key="bls-time-series/pr.txt", Body=r.content)

    # Fetch population JSON
    pop_url = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"
    r = requests.get(pop_url)
    s3.put_object(Bucket=BUCKET, Key="datausa/population.json", Body=r.content)

    return {"status": "Files uploaded"}
