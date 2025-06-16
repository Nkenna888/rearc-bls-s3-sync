import boto3, json, pandas as pd, io, os

s3 = boto3.client("s3")
bucket = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    # Load BLS file
    bls_obj = s3.get_object(Bucket=bucket, Key="bls-time-series/pr.txt")
    df_timeseries = pd.read_csv(io.BytesIO(bls_obj["Body"].read()), sep="\t")
    df_timeseries.columns = df_timeseries.columns.str.strip()
    df_timeseries = df_timeseries.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Load JSON
    pop_obj = s3.get_object(Bucket=bucket, Key="datausa/population.json")
    pop_data = json.loads(pop_obj["Body"].read())
    df_population = pd.json_normalize(pop_data["data"])

    # Filter and join
    df = df_timeseries[
        (df_timeseries["series_id"] == "PRS30006032") & (df_timeseries["period"] == "Q01")
    ][["series_id", "year", "period", "value"]]
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df_population["Year"] = pd.to_numeric(df_population["Year"], errors="coerce")
    df_population["Population"] = pd.to_numeric(df_population["Population"], errors="coerce")

    joined = pd.merge(df, df_population.rename(columns={"Year": "year"}), on="year", how="inner")
    print(joined.head().to_string(index=False))
    return {"status": "Logged results"}
