"""
Basic flow tests for the Firefly Analyzer
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from firefly_analyzer import CloudIacAnalyzer


class TestBasicFlow:
    """Test basic analysis flow"""
    
    def test_missing_resource(self):
        """Test analysis when cloud resource is missing from IaC"""
        analyzer = CloudIacAnalyzer()
        
        cloud_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2"
            }
        ]
        
        iac_resources = []
        
        result = analyzer.analyze(cloud_resources, iac_resources)
        
        assert len(result["analysis"]) == 1
        assert result["analysis"][0]["State"] == "Missing"
        assert result["analysis"][0]["IacResourceItem"] is None
        assert result["analysis"][0]["ChangeLog"] == []
        assert result["summary"]["missing"] == 1
        assert result["summary"]["total"] == 1
    
    def test_exact_match(self):
        """Test analysis when resources match exactly"""
        analyzer = CloudIacAnalyzer()
        
        cloud_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2",
                "config": {"instance_type": "t3.medium"}
            }
        ]
        
        iac_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2",
                "config": {"instance_type": "t3.medium"}
            }
        ]
        
        result = analyzer.analyze(cloud_resources, iac_resources)
        
        assert len(result["analysis"]) == 1
        assert result["analysis"][0]["State"] == "Match"
        assert result["analysis"][0]["ChangeLog"] == []
        assert result["summary"]["match"] == 1
        assert result["summary"]["total"] == 1
    
    def test_modified_resource(self):
        """Test analysis when resources have differences"""
        analyzer = CloudIacAnalyzer()
        
        cloud_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2",
                "tags": {"totalAmount": "17kb", "Environment": "production"}
            }
        ]
        
        iac_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2",
                "tags": {"totalAmount": "22kb", "Environment": "production"}
            }
        ]
        
        result = analyzer.analyze(cloud_resources, iac_resources)
        
        assert len(result["analysis"]) == 1
        assert result["analysis"][0]["State"] == "Modified"
        assert len(result["analysis"][0]["ChangeLog"]) > 0
        assert result["summary"]["modified"] == 1
        assert result["summary"]["total"] == 1
        
        # Check specific change
        change_log = result["analysis"][0]["ChangeLog"]
        total_amount_change = next(
            (change for change in change_log if change["KeyName"] == "tags.totalAmount"), 
            None
        )
        assert total_amount_change is not None
        assert total_amount_change["CloudValue"] == "17kb"
        assert total_amount_change["IacValue"] == "22kb"
    
    def test_analyze_from_files(self):
        """Test analysis from JSON files"""
        analyzer = CloudIacAnalyzer()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as cloud_file:
            cloud_data = [{"id": "test-1", "name": "test-resource"}]
            json.dump(cloud_data, cloud_file)
            cloud_path = cloud_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as iac_file:
            iac_data = [{"id": "test-1", "name": "test-resource"}]
            json.dump(iac_data, iac_file)
            iac_path = iac_file.name
        
        try:
            result = analyzer.analyze_from_files(cloud_path, iac_path)
            assert result["summary"]["match"] == 1
            assert result["summary"]["total"] == 1
        finally:
            # Clean up
            Path(cloud_path).unlink()
            Path(iac_path).unlink()
    
    def test_mixed_scenarios(self):
        """Test analysis with mixed scenarios (match, modified, missing)"""
        analyzer = CloudIacAnalyzer()
        
        cloud_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2"
            },
            {
                "id": "s3-1",
                "type": "aws_s3_bucket",
                "name": "my-bucket",
                "region": "us-east-1",
                "tags": {"Environment": "production"}
            },
            {
                "id": "rds-1",
                "type": "aws_rds_instance",
                "name": "database",
                "region": "us-west-2"
            }
        ]
        
        iac_resources = [
            {
                "id": "ec2-1",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2"
            },
            {
                "id": "s3-1",
                "type": "aws_s3_bucket",
                "name": "my-bucket",
                "region": "us-east-1",
                "tags": {"Environment": "staging"}
            }
        ]
        
        result = analyzer.analyze(cloud_resources, iac_resources)
        
        assert result["summary"]["total"] == 3
        assert result["summary"]["match"] == 1
        assert result["summary"]["modified"] == 1
        assert result["summary"]["missing"] == 1
        
        # Check specific states
        states = [item["State"] for item in result["analysis"]]
        assert "Match" in states
        assert "Modified" in states
        assert "Missing" in states
