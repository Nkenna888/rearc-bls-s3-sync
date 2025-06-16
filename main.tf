# ------------------------------------------
# Terraform for Rearc Part 4 Data Pipeline
# ------------------------------------------


resource "random_id" "suffix" {
  byte_length = 4
}

# ----------------------
# S3 Bucket
# ----------------------
resource "aws_s3_bucket" "data_bucket" {
  bucket        = "rearc-pipeline-bucket-${random_id.suffix.hex}"
  force_destroy = true
}

# ----------------------
# IAM Role for Lambda
# ----------------------
resource "aws_iam_role" "lambda_exec" {
  name = "rearc_lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_sqs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

# ----------------------
# SQS Queue
# ----------------------
resource "aws_sqs_queue" "json_event_queue" {
  name               = "json-event-queue"
  visibility_timeout_seconds = 310
}

resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.json_event_queue.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "sqs:SendMessage",
        Resource  = aws_sqs_queue.json_event_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.data_bucket.arn
          }
        }
      }
    ]
  })
}

# ----------------------
# Lambda 1: Ingest (Part 1 + 2)
# ----------------------
resource "aws_lambda_function" "ingest_lambda" {
  function_name    = "rearc_ingest_lambda"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "ingest_lambda.lambda_handler"
  runtime          = "python3.11"
  filename         = "lambda/ingest_lambda.zip"
  source_code_hash = filebase64sha256("lambda/ingest_lambda.zip")
  timeout          = 300

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data_bucket.bucket
    }
  }
}

# ----------------------
# Lambda 2: Report (Part 3)
# ----------------------
resource "aws_lambda_function" "report_lambda" {
  function_name    = "rearc_report_lambda"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "report_lambda.lambda_handler"
  runtime          = "python3.11"
  filename         = "lambda/report_lambda.zip"
  source_code_hash = filebase64sha256("lambda/report_lambda.zip")
  timeout          = 300

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data_bucket.bucket
    }
  }
}

# ----------------------
# CloudWatch Event → Lambda 1 (Daily)
# ----------------------
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "daily-lambda-trigger"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "IngestLambda"
  arn       = aws_lambda_function.ingest_lambda.arn
}

resource "aws_lambda_permission" "allow_cwe" {
  statement_id  = "AllowExecutionFromCWE"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}

# ----------------------
# S3 → SQS Notification
# ----------------------
resource "aws_s3_bucket_notification" "json_notification" {
  bucket = aws_s3_bucket.data_bucket.id

  queue {
    queue_arn     = aws_sqs_queue.json_event_queue.arn
    events        = ["s3:ObjectCreated:Put"]
    filter_prefix = "datausa/"
    filter_suffix = ".json"
  }

  depends_on = [aws_sqs_queue.json_event_queue, aws_sqs_queue_policy.allow_s3]
}

# ----------------------
# SQS → Lambda 2 Trigger
# ----------------------
resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
  event_source_arn = aws_sqs_queue.json_event_queue.arn
  function_name    = aws_lambda_function.report_lambda.arn
  batch_size       = 1
}

