output "bucket_id" {
  description = "ID of the created S3 bucket"
  value       = aws_s3_bucket.firefly_test_bucket.id
}

output "bucket_arn" {
  description = "ARN of the created S3 bucket"
  value       = aws_s3_bucket.firefly_test_bucket.arn
}

output "bucket_region" {
  description = "Region of the created S3 bucket"
  value       = aws_s3_bucket.firefly_test_bucket.region
}

