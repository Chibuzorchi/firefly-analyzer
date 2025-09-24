"""
Tests for the resource matcher
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from firefly_analyzer.matcher import ResourceMatcher


class TestResourceMatcher:
    """Test resource matching heuristics"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.matcher = ResourceMatcher()
    
    def test_primary_match_by_id(self):
        """Test primary matching by exact ID"""
        cloud_resource = {
            "id": "ec2-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "id": "ec2-456",
                "type": "aws_ec2_instance",
                "name": "db-server"
            },
            {
                "id": "ec2-123",
                "type": "aws_ec2_instance",
                "name": "web-server"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["id"] == "ec2-123"
    
    def test_primary_match_by_resource_id(self):
        """Test primary matching by resource_id"""
        cloud_resource = {
            "resource_id": "ec2-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "resource_id": "ec2-123",
                "type": "aws_ec2_instance",
                "name": "web-server"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["resource_id"] == "ec2-123"
    
    def test_primary_match_by_arn(self):
        """Test primary matching by ARN"""
        cloud_resource = {
            "arn": "arn:aws:ec2:us-west-2:123456789012:instance/i-1234567890abcdef0",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "arn": "arn:aws:ec2:us-west-2:123456789012:instance/i-1234567890abcdef0",
                "type": "aws_ec2_instance",
                "name": "web-server"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["arn"] == cloud_resource["arn"]
    
    def test_secondary_match_by_type_and_name(self):
        """Test secondary matching by type and name tuple"""
        cloud_resource = {
            "id": "cloud-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "id": "iac-456",
                "type": "aws_ec2_instance",
                "name": "web-server"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["type"] == "aws_ec2_instance"
        assert match["name"] == "web-server"
    
    def test_secondary_match_by_resource_type(self):
        """Test secondary matching by resourceType field"""
        cloud_resource = {
            "id": "cloud-123",
            "resourceType": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "id": "iac-456",
                "resourceType": "aws_ec2_instance",
                "name": "web-server"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["resourceType"] == "aws_ec2_instance"
        assert match["name"] == "web-server"
    
    def test_tertiary_match_by_name_and_region(self):
        """Test tertiary matching by name and region"""
        cloud_resource = {
            "id": "cloud-123",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "region": "us-west-2"
        }
        
        iac_resources = [
            {
                "id": "iac-456",
                "type": "aws_ec2_instance",
                "name": "web-server",
                "region": "us-west-2"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["name"] == "web-server"
        assert match["region"] == "us-west-2"
    
    def test_tertiary_match_by_name_only(self):
        """Test tertiary matching by name only (fallback)"""
        cloud_resource = {
            "id": "cloud-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "id": "iac-456",
                "type": "aws_ec2_instance",
                "name": "web-server"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is not None
        assert match["name"] == "web-server"
    
    def test_no_match_found(self):
        """Test when no match is found"""
        cloud_resource = {
            "id": "cloud-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resources = [
            {
                "id": "iac-456",
                "type": "aws_s3_bucket",
                "name": "my-bucket"
            }
        ]
        
        match = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        assert match is None
    
    def test_match_confidence_id_match(self):
        """Test match confidence for ID match"""
        cloud_resource = {
            "id": "ec2-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        iac_resource = {
            "id": "ec2-123",
            "type": "aws_ec2_instance",
            "name": "web-server"
        }
        
        confidence = self.matcher.get_match_confidence(cloud_resource, iac_resource)
        
        assert confidence == 1.0
    
    def test_match_confidence_type_name_match(self):
        """Test match confidence for type and name match"""
        cloud_resource = {
            "id": "cloud-123",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "region": "us-west-2"
        }
        
        iac_resource = {
            "id": "iac-456",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "region": "us-west-2"
        }
        
        confidence = self.matcher.get_match_confidence(cloud_resource, iac_resource)
        
        assert confidence == 1.0  # type + name + region = 0.4 + 0.4 + 0.2 = 1.0
    
    def test_match_confidence_partial_match(self):
        """Test match confidence for partial match"""
        cloud_resource = {
            "id": "cloud-123",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "region": "us-west-2"
        }
        
        iac_resource = {
            "id": "iac-456",
            "type": "aws_ec2_instance",
            "name": "db-server",
            "region": "us-west-2"
        }
        
        confidence = self.matcher.get_match_confidence(cloud_resource, iac_resource)
        
        assert abs(confidence - 0.6) < 0.001  # type + region = 0.4 + 0.2 = 0.6
