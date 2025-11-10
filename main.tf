# Main Terraform configuration - Root level for Firefly detection
# This file is in the root directory so Firefly can easily detect it

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration - Firefly scans S3 buckets for state files
  backend "s3" {
    bucket         = "firefly-terraform-state-1762436058"
    key            = "firefly-test/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
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

# Test S3 Bucket - Root level for Firefly detection
resource "aws_s3_bucket" "firefly_test_bucket_root" {
  bucket = var.bucket_name

  tags = {
    Name        = "Firefly Test Bucket Root"
    Purpose     = "Firefly Integration Testing Root Level"
    ManagedBy   = "Terraform"
    Location    = "Root Directory"
  }
}

# Enable versioning on the bucket
resource "aws_s3_bucket_versioning" "firefly_test_bucket_versioning_root" {
  bucket = aws_s3_bucket.firefly_test_bucket_root.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "firefly_test_bucket_encryption_root" {
  bucket = aws_s3_bucket.firefly_test_bucket_root.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "firefly_test_bucket_pab_root" {
  bucket = aws_s3_bucket.firefly_test_bucket_root.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Additional test resource - EC2 instance (commented out, uncomment if needed)
# resource "aws_instance" "firefly_test_instance" {
#   ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
#   instance_type = "t2.micro"
#   
#   tags = {
#     Name = "Firefly Test Instance"
#   }
# }

