#!/bin/bash
# Quick script to create an unmanaged AWS resource for Firefly testing
# This creates an S3 bucket directly in AWS (not via Terraform)
# Firefly should detect this as "Unmanaged"

set -e

# Generate a unique bucket name
TIMESTAMP=$(date +%s)
BUCKET_NAME="firefly-unmanaged-test-${TIMESTAMP}"
REGION="${AWS_REGION:-us-east-1}"

echo "Creating unmanaged S3 bucket for Firefly testing..."
echo "Bucket name: ${BUCKET_NAME}"
echo "Region: ${REGION}"

# Create the bucket
aws s3 mb "s3://${BUCKET_NAME}" --region "${REGION}"

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket "${BUCKET_NAME}" \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket "${BUCKET_NAME}" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Add tags
aws s3api put-bucket-tagging \
  --bucket "${BUCKET_NAME}" \
  --tagging "TagSet=[
    {Key=Name,Value=Firefly Unmanaged Test},
    {Key=Purpose,Value=Firefly Integration Testing},
    {Key=ManagedBy,Value=Manual}
  ]"

echo ""
echo "✅ Bucket created successfully!"
echo "Bucket name: ${BUCKET_NAME}"
echo "Bucket ARN: arn:aws:s3:::${BUCKET_NAME}"
echo ""
echo "Next steps:"
echo "1. Wait 5-15 minutes for Firefly to detect this resource"
echo "2. Check Firefly UI → Inventory → Unmanaged"
echo "3. You should see this bucket listed as 'Unmanaged'"
echo ""
echo "To clean up later:"
echo "  aws s3 rb s3://${BUCKET_NAME} --force"

