## Rearc Quest - Step 1: BLS Data Sync to AWS S3

This step automates the ingestion of BLS productivity time series data from:

🔗 https://download.bls.gov/pub/time.series/pr/

###  Features

- Uses `requests` and `BeautifulSoup` to scrape available `.txt` and `.dat` files.
- Uploads new or updated files to an S3 bucket under the prefix `bls-time-series/`.
- Deletes stale files in S3 that no longer exist at the source.
- Respects BLS's access policy by providing a `User-Agent` header.
- Avoids redundant uploads and handles dynamic file additions/removals.

###  Script: `step-1.py`


## Run

pip install -r requirements.txt
python step-1.py

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