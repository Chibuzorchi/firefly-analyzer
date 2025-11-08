#!/bin/bash
# Helper script to test Firefly workspace integration locally
# This simulates what would happen in a CI/CD pipeline

set -e

echo "=========================================="
echo "Firefly Workspace Integration Test"
echo "=========================================="
echo ""

# Check if environment variables are set
if [ -z "$FIREFLY_ACCESS_KEY" ] || [ -z "$FIREFLY_SECRET_KEY" ]; then
    echo "❌ Error: FIREFLY_ACCESS_KEY and FIREFLY_SECRET_KEY must be set"
    echo ""
    echo "Get these from Firefly UI → Workspace → Settings → Credentials"
    echo ""
    echo "Export them:"
    echo "  export FIREFLY_ACCESS_KEY='your-access-key'"
    echo "  export FIREFLY_SECRET_KEY='your-secret-key'"
    exit 1
fi

# Get workspace name
WORKSPACE_NAME="${1:-firefly-test-workspace}"
echo "Workspace: ${WORKSPACE_NAME}"
echo ""

# Step 1: Terraform Plan with JSON output
echo "📋 Step 1: Running Terraform Plan..."
terraform plan -json -out=tf.plan > plan_log.jsonl
terraform show -json tf.plan > plan_output.json
echo "✅ Plan complete - outputs saved to plan_log.jsonl and plan_output.json"
echo ""

# Step 2: Download Firefly CLI
echo "⬇️  Step 2: Downloading Firefly CLI..."
if [ ! -f "./fireflyci" ]; then
    curl -O https://gofirefly-prod-iac-ci-cli-binaries.s3.amazonaws.com/fireflyci/latest/fireflyci_Linux_x86_64.tar.gz
    tar -xf fireflyci_Linux_x86_64.tar.gz
    chmod a+x fireflyci
    echo "✅ Firefly CLI downloaded"
else
    echo "✅ Firefly CLI already exists"
fi
echo ""

# Step 3: Firefly Post-Plan
echo "🔍 Step 3: Running Firefly Post-Plan..."
./fireflyci post-plan \
    -l plan_log.jsonl \
    -f plan_output.json \
    --workspace "${WORKSPACE_NAME}"

if [ $? -eq 0 ]; then
    echo "✅ Post-Plan complete - Check Firefly UI for plan visualization"
else
    echo "❌ Post-Plan failed - Check guardrails in Firefly UI"
    exit 1
fi
echo ""

# Step 4: Terraform Apply with JSON output
echo "🚀 Step 4: Running Terraform Apply..."
read -p "Do you want to apply? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Skipping apply..."
    exit 0
fi

terraform apply -auto-approve -json > apply_log.jsonl
echo "✅ Apply complete - output saved to apply_log.jsonl"
echo ""

# Step 5: Firefly Post-Apply
echo "📊 Step 5: Running Firefly Post-Apply..."
./fireflyci post-apply \
    -f apply_log.jsonl \
    --workspace "${WORKSPACE_NAME}"

if [ $? -eq 0 ]; then
    echo "✅ Post-Apply complete - Check Firefly UI for deployment tracking"
else
    echo "❌ Post-Apply failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ Integration Test Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check Firefly UI → Workflows → Workspaces → ${WORKSPACE_NAME}"
echo "2. View the plan visualization"
echo "3. Check deployment history"
echo ""

