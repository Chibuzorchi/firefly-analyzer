variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket to create (must be globally unique)"
  type        = string
  # You'll need to provide this when running terraform apply
  # Example: terraform apply -var="bucket_name=my-unique-firefly-test-bucket-12345"
}

