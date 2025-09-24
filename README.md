# Firefly Asset Management Solution

A comprehensive **Cloud to Infrastructure-as-Code (IaC) Resources Analyzer** that helps DevOps teams identify discrepancies between their actual cloud resources and their IaC definitions.

## 🚀 Features

- **Multi-level Resource Matching**: Primary (ID), Secondary (type+name), and Tertiary (name+region) matching heuristics
- **Deep Difference Detection**: Uses `deepdiff` to detect nested property changes
- **Comprehensive Change Logging**: Detailed change reports with dot-notation paths
- **S3 Integration**: Upload analysis reports to S3 (including LocalStack support)
- **CLI Interface**: Easy-to-use command-line interface
- **Docker Support**: Containerized deployment with LocalStack integration
- **Extensive Testing**: 100% test coverage with pytest

## 📋 Requirements

- Python 3.10+
- Docker & Docker Compose (for LocalStack integration)
- AWS credentials (for real S3) or LocalStack (for testing)

## 🛠️ Installation

### Option 1: Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd firefly-analyzer
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

### Option 2: Docker

1. **Build and run with LocalStack:**
   ```bash
   docker-compose up --build
   ```

## 🎯 Usage

### Basic Analysis

```bash
# Analyze cloud resources against IaC definitions
python -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --output analysis_report.json \
  --verbose
```

### S3 Upload (LocalStack)

```bash
# Start LocalStack
docker-compose up localstack -d

# Run analysis with S3 upload
python -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --upload-s3 firefly-analysis-reports \
  --s3-key analysis-report.json \
  --localstack-endpoint http://localhost:4566 \
  --verbose
```

### S3 Operations

```bash
# List available S3 buckets
python -m firefly_analyzer.cli list-buckets \
  --localstack-endpoint http://localhost:4566

# Download analysis report from S3
python -m firefly_analyzer.cli download \
  --bucket firefly-analysis-reports \
  --key analysis-report.json \
  --localstack-endpoint http://localhost:4566 \
  --output downloaded_report.json
```

## 📊 Analysis Output

The analyzer produces a comprehensive report with the following structure:

```json
{
  "analysis": [
    {
      "CloudResourceItem": { /* Full cloud resource object */ },
      "IacResourceItem": { /* Matching IaC resource or null */ },
      "State": "Missing" | "Match" | "Modified",
      "ChangeLog": [
        {
          "KeyName": "tags.totalAmount",
          "CloudValue": "17kb",
          "IacValue": "22kb"
        }
      ]
    }
  ],
  "summary": {
    "total": 3,
    "missing": 1,
    "modified": 1,
    "match": 1
  }
}
```

## 🔍 Matching Heuristics

The analyzer uses a three-tier matching strategy:

1. **Primary Match**: Exact match on `id`, `resource_id`, or `arn`
2. **Secondary Match**: Exact match on `(type/resourceType, name)` tuple
3. **Tertiary Match**: Fallback match on `name` and `region`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/firefly_analyzer --cov-report=html

# Run specific test file
pytest tests/test_basic_flow.py -v
```

### Test Categories

- **Basic Flow Tests**: Missing, match, and modified scenarios
- **Matcher Tests**: Resource matching heuristics
- **Diff Converter Tests**: Change log generation
- **CLI Tests**: Command-line interface functionality

## 🚀 GitHub Actions

This project includes comprehensive GitHub Actions workflows for CI/CD:

### Workflows

- **CI** (`.github/workflows/ci.yml`): Runs on every push and PR
  - Tests across Python 3.10, 3.11, and 3.12
  - Linting with flake8, black, and mypy
  - Code coverage reporting
  - Docker image building and testing
  - Integration tests with LocalStack

- **Release** (`.github/workflows/release.yml`): Automated releases
  - Publishes to PyPI on version tags
  - Builds and pushes Docker images to Docker Hub
  - Creates GitHub releases with changelogs

- **Docker** (`.github/workflows/docker.yml`): Docker image management
  - Multi-platform builds (AMD64, ARM64)
  - Security scanning with Trivy
  - Automated tagging

- **Security** (`.github/workflows/security.yml`): Security scanning
  - Dependency vulnerability scanning
  - CodeQL analysis
  - Docker image security scanning

- **Scheduled Analysis** (`.github/workflows/scheduled-analysis.yml`): Automated analysis
  - Runs weekly analysis
  - Uploads reports to S3
  - Can be triggered manually

### Setup Requirements

To use the GitHub Actions workflows, you'll need to configure these secrets:

#### Required Secrets
- `PYPI_API_TOKEN`: PyPI API token for publishing packages
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

#### Optional Secrets (for S3 integration)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region
- `S3_BUCKET`: S3 bucket name for analysis reports

### Workflow Triggers

- **Push to main/develop**: Runs CI, Docker build, and security scans
- **Pull Request**: Runs CI and Docker build (no push)
- **Version tags (v*)**: Triggers release workflow
- **Manual dispatch**: All workflows can be triggered manually
- **Scheduled**: Security scans run weekly, analysis runs weekly

### Badges

Add these badges to your README:

```markdown
![CI](https://github.com/Chibuzorchi/firefly-analyzer/workflows/CI/badge.svg)
![Release](https://github.com/Chibuzorchi/firefly-analyzer/workflows/Release/badge.svg)
![Security](https://github.com/Chibuzorchi/firefly-analyzer/workflows/Security/badge.svg)
```

## 🐳 Docker Integration

### LocalStack Setup

The project includes a complete LocalStack setup for S3 testing:

```bash
# Start LocalStack with S3
docker-compose up localstack -d

# Check LocalStack status
curl http://localhost:4566/health
```

### Full Stack Testing

```bash
# Run complete analysis with LocalStack S3
docker-compose up --build
```

## 📁 Project Structure

```
firefly-analyzer/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── samples/
│   ├── cloud_resources.json
│   └── iac_resources.json
├── src/firefly_analyzer/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── analyzer.py         # Main orchestration
│   ├── matcher.py          # Resource matching
│   ├── diff_converter.py   # Change log generation
│   ├── s3_uploader.py      # S3 integration
│   └── utils.py            # Utilities
└── tests/
    ├── test_basic_flow.py
    ├── test_matcher.py
    ├── test_diff_converter.py
    └── test_cli.py
```

## 🔧 Configuration

### Environment Variables

- `AWS_ENDPOINT_URL`: S3 endpoint URL (for LocalStack)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region

### Sample Data

The `samples/` directory contains example JSON files:

- **cloud_resources.json**: Sample cloud resources
- **iac_resources.json**: Sample IaC definitions

## 🚀 Advanced Usage

### Custom Matching Logic

```python
from firefly_analyzer import CloudIacAnalyzer, ResourceMatcher

# Create custom matcher
matcher = ResourceMatcher()
analyzer = CloudIacAnalyzer()

# Use custom matching logic
matching_iac = matcher.find_matching_iac_resource(cloud_resource, iac_resources)
```

### Programmatic Analysis

```python
from firefly_analyzer import CloudIacAnalyzer

analyzer = CloudIacAnalyzer()
report = analyzer.analyze(cloud_resources, iac_resources)

# Get detailed changes
changes = analyzer.get_detailed_changes(report['analysis'])
```

## 🐛 Troubleshooting

### Common Issues

1. **LocalStack not ready**: Wait 15-30 seconds after starting LocalStack
2. **S3 bucket not found**: Ensure bucket exists or use `create_bucket_if_not_exists`
3. **Import errors**: Ensure `PYTHONPATH` includes the `src` directory

### Debug Mode

```bash
# Enable verbose output
python -m firefly_analyzer.cli analyze --cloud file.json --iac file.json --verbose
```

## 📈 Performance

- **Small datasets** (< 100 resources): < 1 second
- **Medium datasets** (100-1000 resources): 1-5 seconds
- **Large datasets** (1000+ resources): 5-30 seconds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🎯 Roadmap

- [ ] Support for more cloud providers (Azure, GCP)
- [ ] Terraform state file integration
- [ ] Web UI dashboard
- [ ] Real-time monitoring
- [ ] API endpoints for integration

---

**Built with ❤️ for DevOps teams who value infrastructure consistency**
