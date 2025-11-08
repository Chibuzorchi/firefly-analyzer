# Test Terraform configuration for Firefly integration
# This creates an S3 bucket that Firefly can detect and track

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration - Firefly scans S3 buckets for state files
  # Replace with your actual S3 bucket name for state storage
  backend "s3" {
    bucket         = "firefly-terraform-state-1762436058"  # Your state bucket
    key            = "firefly-test/terraform.tfstate"
    region         = "us-east-1"  # Your region
    encrypt        = true
    # dynamodb_table = "terraform-state-lock"  # Optional: for state locking
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      ManagedBy     = "Terraform"
      Environment   = "test"
      Project       = "firefly-test"
      CreatedBy     = "firefly-integration-test"
    }
  }
}

# Test S3 Bucket - This will be detected by Firefly as "Codified" if state is found
resource "aws_s3_bucket" "firefly_test_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "Firefly Test Bucket"
    Purpose     = "Firefly Integration Testing"
    ManagedBy   = "Terraform"
  }
}

# Enable versioning on the bucket
resource "aws_s3_bucket_versioning" "firefly_test_bucket_versioning" {
  bucket = aws_s3_bucket.firefly_test_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "firefly_test_bucket_encryption" {
  bucket = aws_s3_bucket.firefly_test_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "firefly_test_bucket_pab" {
  bucket = aws_s3_bucket.firefly_test_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

