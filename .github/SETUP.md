# GitHub Actions Setup Guide

This guide will help you set up GitHub Actions for the Firefly Analyzer project.

## Prerequisites

1. A GitHub repository (forked or your own)
2. Required accounts and tokens:
   - PyPI account (for package publishing)
   - Docker Hub account (for container images)
   - AWS account (optional, for S3 integration)

## Step 1: Configure Repository Secrets

Go to your repository → Settings → Secrets and variables → Actions, and add the following secrets:

### Required Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `PYPI_API_TOKEN` | PyPI API token for publishing packages | 1. Go to [PyPI](https://pypi.org) → Account Settings → API tokens<br>2. Create a new token with "Upload packages" scope |
| `DOCKER_USERNAME` | Your Docker Hub username | Your Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password or access token | Your Docker Hub password or create an access token |

### Optional Secrets (for S3 integration)

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `AWS_ACCESS_KEY_ID` | AWS access key | AWS IAM → Users → Security credentials → Access keys |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Same as above |
| `AWS_DEFAULT_REGION` | AWS region (e.g., us-east-1) | Choose your preferred region |
| `S3_BUCKET` | S3 bucket name for analysis reports | Create an S3 bucket in your AWS account |

## Step 2: Enable GitHub Actions

1. Go to your repository → Actions tab
2. Click "I understand my workflows, go ahead and enable them"
3. The workflows will automatically run on the next push

## Step 3: Test the Setup

### Test CI Workflow
1. Make a small change to any file
2. Commit and push to the `main` or `develop` branch
3. Go to Actions tab to see the CI workflow running

### Test Release Workflow
1. Create a new tag: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. This will trigger the release workflow

### Test Manual Workflows
1. Go to Actions tab
2. Select any workflow
3. Click "Run workflow" button
4. Choose the branch and click "Run workflow"

## Step 4: Customize Workflows (Optional)

### Modify Python Versions
Edit `.github/workflows/ci.yml`:
```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11, 3.12]  # Add or remove versions
```

### Modify Schedule
Edit `.github/workflows/scheduled-analysis.yml`:
```yaml
schedule:
  - cron: '0 9 * * 1'  # Change to your preferred schedule
```

### Add Notifications
Add notification steps to workflows:
```yaml
- name: Notify on success
  uses: 8398a7/action-slack@v3
  with:
    status: success
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Step 5: Monitor and Maintain

### Check Workflow Status
- Go to Actions tab to see all workflow runs
- Click on any workflow to see detailed logs
- Check the "Checks" tab on PRs to see CI status

### Handle Failures
- If a workflow fails, check the logs for error details
- Common issues:
  - Missing secrets
  - Incorrect file paths
  - Dependency conflicts
  - Permission issues

### Update Dependencies
- Dependabot will create PRs for dependency updates
- Review and merge PRs to keep dependencies current
- Check security advisories regularly

## Troubleshooting

### Common Issues

1. **"Resource not accessible by integration"**
   - Check if secrets are properly configured
   - Verify token permissions

2. **"Docker build failed"**
   - Check Dockerfile syntax
   - Verify base image availability

3. **"PyPI upload failed"**
   - Verify PyPI token has correct permissions
   - Check if package version already exists

4. **"S3 upload failed"**
   - Verify AWS credentials
   - Check S3 bucket permissions
   - Ensure bucket exists

### Getting Help

- Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
- Review workflow logs for specific error messages
- Open an issue in this repository for project-specific problems

## Security Best Practices

1. **Never commit secrets** to your repository
2. **Use least privilege** for tokens and access keys
3. **Regularly rotate** secrets and tokens
4. **Review workflow permissions** before enabling
5. **Monitor workflow runs** for suspicious activity

## Next Steps

Once GitHub Actions is set up:

1. **Set up branch protection rules** to require CI checks
2. **Configure status checks** for PRs
3. **Set up notifications** for workflow failures
4. **Create custom workflows** for your specific needs
5. **Monitor and optimize** workflow performance
