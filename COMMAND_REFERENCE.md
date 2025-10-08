# Firefly Analyzer - Complete Command Reference

##  Basic Analysis Commands

### 1. Basic Analysis (Local Only)
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --output analysis_report.json \
  --verbose
```

### 2. Analysis with S3 Upload (LocalStack)
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --output analysis_report.json \
  --upload-s3 firefly-analysis-reports \
  --s3-key analysis-report.json \
  --localstack-endpoint http://localhost:4566 \
  --verbose
```


### 3. Analysis with S3 Upload (Real AWS)
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --output analysis_report.json \
  --upload-s3 your-bucket-name \
  --s3-key analysis-report.json \
  --verbose
```

### 4. Quick Analysis (No Output File)
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --verbose
```

### 5. Silent Analysis (No Verbose Output)
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --output analysis_report.json
```

## S3 Download Commands

### 6. Download Report from S3 (LocalStack)
```bash
python3 -m firefly_analyzer.cli download \
  --bucket firefly-analysis-reports \
  --key analysis-report.json \
  --localstack-endpoint http://localhost:4566 \
  --output downloaded_report.json
```

### 7. Download Report from S3 (Real AWS)
```bash
python3 -m firefly_analyzer.cli download \
  --bucket your-bucket-name \
  --key analysis-report.json \
  --output downloaded_report.json
```

### 8. Download and Display (No File Save)
```bash
python3 -m firefly_analyzer.cli download \
  --bucket firefly-analysis-reports \
  --key analysis-report.json \
  --localstack-endpoint http://localhost:4566
```

## S3 Management Commands

### 9. List S3 Buckets (LocalStack)
```bash
python3 -m firefly_analyzer.cli list-buckets \
  --localstack-endpoint http://localhost:4566
```

### 10. List S3 Buckets (Real AWS)
```bash
python3 -m firefly_analyzer.cli list-buckets
```

## 🧪 Testing Commands

### 11. Run All Tests
```bash
pytest tests/ -v
```

### 12. Run Tests with Coverage
```bash
pytest tests/ --cov=src/firefly_analyzer --cov-report=html
```

### 13. Run Specific Test Files
```bash
# Basic flow tests
pytest tests/test_basic_flow.py -v

# CLI tests
pytest tests/test_cli.py -v

# Matcher tests
pytest tests/test_matcher.py -v

# Diff converter tests
pytest tests/test_diff_converter.py -v
```

### 14. Run Tests with Coverage Report
```bash
pytest tests/ --cov=src/firefly_analyzer --cov-report=html --cov-report=term
```

## 🐳 Docker Commands

### 15. Start LocalStack Only
```bash
docker-compose up localstack -d
```

### 16. Start Full Stack (LocalStack + Analyzer)
```bash
docker-compose up --build
```

### 17. Stop All Services
```bash
docker-compose down
```

### 18. Check LocalStack Health
```bash
curl http://localhost:4566/health
```

## 🔧 Development Commands

### 19. Install Package in Development Mode
```bash
pip install -e .
```

### 20. Install Dependencies
```bash
pip install -r requirements.txt
```

### 21. Run with Python Module
```bash
python -m firefly_analyzer.cli --help
```

### 22. Check CLI Help
```bash
python3 -m firefly_analyzer.cli --help
python3 -m firefly_analyzer.cli analyze --help
python3 -m firefly_analyzer.cli download --help
python3 -m firefly_analyzer.cli list-buckets --help
```

## 📊 Report Analysis Commands

### 23. View Analysis Report
```bash
cat analysis_report.json
```

### 24. Pretty Print JSON
```bash
cat analysis_report.json | python3 -m json.tool
```

### 25. View Downloaded Report
```bash
cat downloaded_report.json
```

## 🔍 State-Specific Analysis Commands

### 26. Show Only Matches
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
matches = [item for item in data['analysis'] if item['State'] == 'Match']
print('✅ MATCHES ONLY:')
print(f'Count: {len(matches)}')
for match in matches:
    print(f'  • {match[\"CloudResourceItem\"].get(\"name\", \"unknown\")} ({match[\"CloudResourceItem\"].get(\"id\", \"unknown\")})')
"
```

### 27. Show Only Modified
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
modified = [item for item in data['analysis'] if item['State'] == 'Modified']
print('⚠️  MODIFIED ONLY:')
print(f'Count: {len(modified)}')
for mod in modified:
    print(f'  • {mod[\"CloudResourceItem\"].get(\"name\", \"unknown\")} ({mod[\"CloudResourceItem\"].get(\"id\", \"unknown\")})')
    for change in mod['ChangeLog']:
        print(f'    - {change[\"KeyName\"]}: \"{change[\"IacValue\"]}\" → \"{change[\"CloudValue\"]}\"')
"
```

### 28. Show Only Missing
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
missing = [item for item in data['analysis'] if item['State'] == 'Missing']
print('❌ MISSING ONLY:')
print(f'Count: {len(missing)}')
for miss in missing:
    print(f'  • {miss[\"CloudResourceItem\"].get(\"name\", \"unknown\")} ({miss[\"CloudResourceItem\"].get(\"id\", \"unknown\")})')
"
```

### 29. Count by State
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
states = {}
for item in data['analysis']:
    state = item['State']
    states[state] = states.get(state, 0) + 1
print('📊 STATE BREAKDOWN:')
for state, count in states.items():
    emoji = {'Match': '✅', 'Modified': '⚠️', 'Missing': '❌'}.get(state, '❓')
    print(f'{emoji} {state}: {count}')
"
```

### 30. Show Resources with Changes
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
changed = [item for item in data['analysis'] if item['ChangeLog']]
print('🔍 RESOURCES WITH CHANGES:')
print(f'Count: {len(changed)}')
for item in changed:
    print(f'  • {item[\"CloudResourceItem\"].get(\"name\", \"unknown\")} ({item[\"State\"]})')
    for change in item['ChangeLog']:
        print(f'    - {change[\"KeyName\"]}: \"{change[\"IacValue\"]}\" → \"{change[\"CloudValue\"]}\"')
"
```

### 31. Show Perfect Matches (No Changes)
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
perfect = [item for item in data['analysis'] if item['State'] == 'Match' and not item['ChangeLog']]
print('🎯 PERFECT MATCHES:')
print(f'Count: {len(perfect)}')
for match in perfect:
    print(f'  • {match[\"CloudResourceItem\"].get(\"name\", \"unknown\")} ({match[\"CloudResourceItem\"].get(\"id\", \"unknown\")})')
"
```

### 32. Show Resources by Type
```bash
python3 -c "
import json
from collections import defaultdict
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
by_type = defaultdict(list)
for item in data['analysis']:
    resource_type = item['CloudResourceItem'].get('type', 'unknown')
    by_type[resource_type].append(item)
print('📋 RESOURCES BY TYPE:')
for resource_type, items in by_type.items():
    print(f'  {resource_type}: {len(items)}')
    for item in items:
        state = item['State']
        emoji = {'Match': '✅', 'Modified': '⚠️', 'Missing': '❌'}.get(state, '❓')
        print(f'    {emoji} {item[\"CloudResourceItem\"].get(\"name\", \"unknown\")} ({state})')
"
```

### 33. Generate State-Specific Reports
```bash
# Generate separate files for each state
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)

# Matches only
matches = [item for item in data['analysis'] if item['State'] == 'Match']
with open('matches_only.json', 'w') as f:
    json.dump({'analysis': matches, 'summary': {'total': len(matches), 'match': len(matches), 'modified': 0, 'missing': 0}}, f, indent=2)

# Modified only
modified = [item for item in data['analysis'] if item['State'] == 'Modified']
with open('modified_only.json', 'w') as f:
    json.dump({'analysis': modified, 'summary': {'total': len(modified), 'match': 0, 'modified': len(modified), 'missing': 0}}, f, indent=2)

# Missing only
missing = [item for item in data['analysis'] if item['State'] == 'Missing']
with open('missing_only.json', 'w') as f:
    json.dump({'analysis': missing, 'summary': {'total': len(missing), 'match': 0, 'modified': 0, 'missing': len(missing)}}, f, indent=2)

print('✅ Generated separate reports:')
print('  • matches_only.json')
print('  • modified_only.json')
print('  • missing_only.json')
"
```

### 34. Quick State Summary
```bash
python3 -c "
import json
with open('analysis_report.json', 'r') as f:
    data = json.load(f)
summary = data['summary']
print('📊 QUICK SUMMARY:')
print(f'Total: {summary[\"total\"]} | Match: {summary[\"match\"]} | Modified: {summary[\"modified\"]} | Missing: {summary[\"missing\"]}')
"
```

## 🎯 Demo Scenarios

### 26. Demo 1: Show All States (Current Setup)
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --output demo_all_states.json \
  --verbose
```
**Expected Result**: 0 Match, 1 Modified, 2 Missing

### 27. Demo 2: With S3 Integration
```bash
# Start LocalStack
docker-compose up localstack -d
sleep 30

# Run analysis with S3
python3 -m firefly_analyzer.cli analyze \
  --cloud samples/cloud_resources.json \
  --iac samples/iac_resources.json \
  --upload-s3 firefly-demo-reports \
  --s3-key demo-analysis.json \
  --localstack-endpoint http://localhost:4566 \
  --verbose

# List buckets
python3 -m firefly_analyzer.cli list-buckets \
  --localstack-endpoint http://localhost:4566

# Download report
python3 -m firefly_analyzer.cli download \
  --bucket firefly-demo-reports \
  --key demo-analysis.json \
  --localstack-endpoint http://localhost:4566 \
  --output demo_downloaded.json
```

### 28. Demo 3: Test Coverage
```bash
pytest tests/ --cov=src/firefly_analyzer --cov-report=html
echo "Open htmlcov/index.html in your browser to see coverage report"
```

## 🚨 Troubleshooting Commands

### 29. Check Python Path
```bash
python3 -c "import sys; print(sys.path)"
```

### 30. Check Package Installation
```bash
pip list | grep firefly
```

### 31. Check Docker Status
```bash
docker ps
docker-compose ps
```

### 32. Check LocalStack Logs
```bash
docker-compose logs localstack
```

### 33. Clean Docker
```bash
docker-compose down
docker system prune -f
```

## 📝 File Management Commands

### 34. Create Backup of Samples
```bash
cp samples/cloud_resources.json samples/cloud_resources_backup.json
cp samples/iac_resources.json samples/iac_resources_backup.json
```

### 35. Restore Backup
```bash
cp samples/cloud_resources_backup.json samples/cloud_resources.json
cp samples/iac_resources_backup.json samples/iac_resources.json
```

### 36. List All Generated Reports
```bash
ls -la *.json
```

## 🎨 Customization Commands

### 37. Analyze Custom Files
```bash
python3 -m firefly_analyzer.cli analyze \
  --cloud your_cloud_file.json \
  --iac your_iac_file.json \
  --output custom_report.json \
  --verbose
```

### 38. Batch Analysis Script
```bash
# Create a script to analyze multiple file pairs
for i in {1..5}; do
  python3 -m firefly_analyzer.cli analyze \
    --cloud "samples/cloud_${i}.json" \
    --iac "samples/iac_${i}.json" \
    --output "report_${i}.json" \
    --verbose
done
```

## 📋 Quick Reference

| Command Type | Purpose | Key Flags |
|--------------|---------|-----------|
| Basic Analysis | Compare resources | `--cloud`, `--iac`, `--output` |
| S3 Upload | Save to cloud | `--upload-s3`, `--s3-key` |
| S3 Download | Get from cloud | `--bucket`, `--key` |
| S3 List | See buckets | `--localstack-endpoint` |
| Testing | Verify code | `pytest tests/` |
| Docker | Run containers | `docker-compose up` |
| Help | Get assistance | `--help` |

## 🔍 Expected Results by Scenario

### Current Sample Files:
- **Total**: 3 resources
- **Match**: 0
- **Modified**: 1 (EC2 instance with different tag values)
- **Missing**: 2 (S3 bucket and RDS instance)

### After Modifications (see modifications_for_mixed_results.json):
- **Total**: 5 resources
- **Match**: 2
- **Modified**: 2
- **Missing**: 1

---

**💡 Pro Tip**: Save this file and use it as your quick reference guide for all Firefly Analyzer commands!
