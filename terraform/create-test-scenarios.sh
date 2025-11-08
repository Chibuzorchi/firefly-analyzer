#!/bin/bash
# Script to create test scenarios for Firefly: Unmanaged, Ghost, and Drift

set -e

echo "=========================================="
echo "Firefly Test Scenarios Setup"
echo "=========================================="
echo ""

# Scenario 1: Create Unmanaged Resource
echo "📦 Scenario 1: Creating Unmanaged Resource..."
UNMANAGED_BUCKET="firefly-unmanaged-test-$(date +%s)"
echo "   Bucket name: ${UNMANAGED_BUCKET}"

aws s3 mb s3://${UNMANAGED_BUCKET} --region us-east-1 2>&1 | grep -v "make_bucket" || true

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${UNMANAGED_BUCKET} \
  --versioning-configuration Status=Enabled 2>&1 | grep -v "versioning" || true

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ${UNMANAGED_BUCKET} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }' 2>&1 | grep -v "encryption" || true

# Add tags
aws s3api put-bucket-tagging \
  --bucket ${UNMANAGED_BUCKET} \
  --tagging "TagSet=[
    {Key=Name,Value=Firefly Unmanaged Test},
    {Key=Purpose,Value=Testing Unmanaged Detection},
    {Key=ManagedBy,Value=Manual}
  ]" 2>&1 | grep -v "tagging" || true

echo "   ✅ Unmanaged bucket created: ${UNMANAGED_BUCKET}"
echo ""

# Scenario 2: Create Ghost Resource (Create in Terraform, then delete from AWS)
echo "👻 Scenario 2: Creating Ghost Resource..."
echo "   Step 1: Creating bucket via Terraform..."

# First, we need to add it to Terraform
# This is a bit complex, so we'll create it first, then delete from AWS
GHOST_BUCKET_NAME="firefly-ghost-test-$(date +%s)"

# Create via Terraform (you'll need to add this to main.tf first)
echo "   ⚠️  Note: You need to add this resource to main.tf:"
echo "   resource \"aws_s3_bucket\" \"ghost_test_bucket\" {"
echo "     bucket = \"${GHOST_BUCKET_NAME}\""
echo "     tags = {"
echo "       Name = \"Firefly Ghost Test\""
echo "       Purpose = \"Testing Ghost Detection\""
echo "     }"
echo "   }"
echo ""
echo "   Then run: terraform apply -var=\"bucket_name=firefly-test-XXXXX\""
echo "   After it's created, delete it from AWS:"
echo "   aws s3 rb s3://${GHOST_BUCKET_NAME} --force"
echo ""

# Scenario 3: Create Drift
echo "🔄 Scenario 3: Creating Drift..."
EXISTING_BUCKET="firefly-test-1762436722"

echo "   Modifying existing bucket: ${EXISTING_BUCKET}"

# Disable versioning (if it was enabled)
echo "   Disabling versioning..."
aws s3api put-bucket-versioning \
  --bucket ${EXISTING_BUCKET} \
  --versioning-configuration Status=Suspended 2>&1 | grep -v "versioning" || true

# Change tags
echo "   Changing tags..."
aws s3api put-bucket-tagging \
  --bucket ${EXISTING_BUCKET} \
  --tagging "TagSet=[
    {Key=Name,Value=Modified Manually for Drift Test},
    {Key=DriftTest,Value=true},
    {Key=ModifiedAt,Value=$(date -u +%Y-%m-%dT%H:%M:%SZ)}
  ]" 2>&1 | grep -v "tagging" || true

echo "   ✅ Drift created - versioning disabled and tags changed"
echo ""

echo "=========================================="
echo "✅ Test Scenarios Created!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  📦 Unmanaged: ${UNMANAGED_BUCKET}"
echo "  👻 Ghost: Add to Terraform, create, then delete from AWS"
echo "  🔄 Drift: ${EXISTING_BUCKET} (versioning disabled, tags changed)"
echo ""
echo "Next Steps:"
echo "1. Wait 5-15 minutes for Firefly to scan"
echo "2. Check Firefly UI:"
echo "   - Inventory → Unmanaged (should see ${UNMANAGED_BUCKET})"
echo "   - Inventory → Drift (should see ${EXISTING_BUCKET})"
echo "   - Inventory → Ghost (after you create and delete the ghost resource)"
echo ""
echo "To clean up later:"
echo "  aws s3 rb s3://${UNMANAGED_BUCKET} --force"
echo "  terraform apply -var=\"bucket_name=firefly-test-1762436722\"  # Fix drift"

