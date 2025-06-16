## Rearc Quest - Step 1: BLS Data Sync to AWS S3

This Python script downloads public time series data from the Bureau of Labor Statistics (BLS) and keeps an S3 bucket in sync with it.

## Features

- Scrapes all `.txt` and `.dat` files from [BLS public dataset](https://download.bls.gov/pub/time.series/pr/)
- Uses AWS S3 to store data
- Avoids re-uploading existing files
- Deletes S3 files no longer found in the source

## Setup

1. Create and configure your S3 bucket.
2. Set your AWS credentials with `aws configure` or environment variables.
3. Replace placeholders in `sync_bls_to_s3.py`:
   - `S3_BUCKET = 'rearc-bls-yourname'`
   - `USER_AGENT = 'Your Name (your.email@example.com)'`

## Output

The following is a direct URL to one of the synced files:

📄 [pr.txt](https://rearc-bls-nahom.s3.amazonaws.com/bls-time-series/pr.txt)


## Run

pip install -r requirements.txt
python sync_bls_to_s3.py

---

## Part 2 - DataUSA API

This script fetches national population data from DataUSA and saves it to S3 as a JSON file.

**API Endpoint:**  
https://datausa.io/api/data?drilldowns=Nation&measures=Population

**S3 URL (public):**  
https://rearc-bls-nahom.s3.amazonaws.com/datausa/population.json

---

## Part 3 – Data Analytics

This notebook performs population and time-series analytics using data sourced in Parts 1 and 2.

### Objectives Covered

1. **Population Statistics (2013–2018)**  
   - Calculated mean and standard deviation of annual U.S. population  
   - Data sourced from `population.json` (DataUSA API)

2. **Best Year per Series ID**  
   - For each `series_id`, identified the year with the highest sum of quarterly `value`s  
   - Grouped and aggregated time-series from `pr.data.0.Current`

3. **Joined Report: Value + Population**  
   - Filtered `PRS30006032` for `Q01`  
   - Joined with population data by year  
   - Produced a final report containing `series_id`, `year`, `period`, `value`, and `Population`

### Notebook

- File: [`rearc_part3_analysis.ipynb`](./rearc_part3_analysis.ipynb)

---

## Step 4: Terraform Pipeline
- Automates:
  - Ingest lambda (Part 1 & 2)
  - S3-to-SQS notification
  - SQS-to-report lambda trigger (Part 3)
  - Daily trigger via CloudWatch
- To deploy:

cd terraform/
terraform init
terraform apply