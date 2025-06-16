output "bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}

output "ingest_lambda_name" {
  value = aws_lambda_function.ingest_lambda.function_name
}

output "report_lambda_name" {
  value = aws_lambda_function.report_lambda.function_name
}

output "sqs_queue_url" {
  value = aws_sqs_queue.json_event_queue.id
}
