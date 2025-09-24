"""
Tests for the diff converter
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from firefly_analyzer.diff_converter import DiffConverter


class TestDiffConverter:
    """Test diff conversion to ChangeLog format"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.converter = DiffConverter()
    
    def test_identical_resources(self):
        """Test conversion with identical resources"""
        cloud_resource = {
            "id": "ec2-1",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "tags": {"Environment": "production"}
        }
        
        iac_resource = {
            "id": "ec2-1",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "tags": {"Environment": "production"}
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        assert changelog == []
    
    def test_simple_value_change(self):
        """Test conversion with simple value change"""
        cloud_resource = {
            "id": "ec2-1",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "tags": {"totalAmount": "17kb"}
        }
        
        iac_resource = {
            "id": "ec2-1",
            "type": "aws_ec2_instance",
            "name": "web-server",
            "tags": {"totalAmount": "22kb"}
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        assert len(changelog) == 1
        assert changelog[0]["KeyName"] == "tags.totalAmount"
        assert changelog[0]["CloudValue"] == "17kb"
        assert changelog[0]["IacValue"] == "22kb"
    
    def test_nested_property_change(self):
        """Test conversion with nested property change"""
        cloud_resource = {
            "id": "ec2-1",
            "config": {
                "instance_type": "t3.large",
                "size": "100GB"
            }
        }
        
        iac_resource = {
            "id": "ec2-1",
            "config": {
                "instance_type": "t3.medium",
                "size": "100GB"
            }
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        assert len(changelog) == 1
        assert changelog[0]["KeyName"] == "config.instance_type"
        assert changelog[0]["CloudValue"] == "t3.large"
        assert changelog[0]["IacValue"] == "t3.medium"
    
    def test_dictionary_item_added(self):
        """Test conversion with added dictionary item"""
        cloud_resource = {
            "id": "ec2-1",
            "tags": {
                "Environment": "production",
                "Owner": "devops-team"
            }
        }
        
        iac_resource = {
            "id": "ec2-1",
            "tags": {
                "Environment": "production"
            }
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        assert len(changelog) == 1
        assert changelog[0]["KeyName"] == "tags.Owner"
        assert changelog[0]["CloudValue"] == "ADDED"
        assert changelog[0]["IacValue"] is None
    
    def test_dictionary_item_removed(self):
        """Test conversion with removed dictionary item"""
        cloud_resource = {
            "id": "ec2-1",
            "tags": {
                "Environment": "production"
            }
        }
        
        iac_resource = {
            "id": "ec2-1",
            "tags": {
                "Environment": "production",
                "Owner": "devops-team"
            }
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        assert len(changelog) == 1
        assert changelog[0]["KeyName"] == "tags.Owner"
        assert changelog[0]["CloudValue"] is None
        assert changelog[0]["IacValue"] == "REMOVED"
    
    def test_type_change(self):
        """Test conversion with type change"""
        cloud_resource = {
            "id": "ec2-1",
            "config": {
                "size": 100
            }
        }
        
        iac_resource = {
            "id": "ec2-1",
            "config": {
                "size": "100GB"
            }
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        assert len(changelog) == 1
        assert changelog[0]["KeyName"] == "config.size"
        assert "int: 100" in changelog[0]["CloudValue"]
        assert "str: 100GB" in changelog[0]["IacValue"]
    
    def test_array_differences(self):
        """Test conversion with array differences"""
        cloud_resource = {
            "id": "ec2-1",
            "security_groups": ["sg-12345", "sg-67890", "sg-11111"]
        }
        
        iac_resource = {
            "id": "ec2-1",
            "security_groups": ["sg-12345", "sg-67890"]
        }
        
        changelog = self.converter.convert_diff_to_changelog(cloud_resource, iac_resource)
        
        # Should have changes for the array
        array_changes = [change for change in changelog if "security_groups" in change["KeyName"]]
        assert len(array_changes) > 0
        
        # Check that we have changes for the new item (deepdiff breaks strings into chars)
        new_item_changes = [change for change in array_changes if "2[+]" in change["KeyName"]]
        assert len(new_item_changes) > 0
    
    def test_compare_arrays_with_id_matching(self):
        """Test array comparison with ID matching"""
        cloud_array = [
            {"id": "sg-1", "name": "web-sg", "ports": [80, 443]},
            {"id": "sg-2", "name": "db-sg", "ports": [5432]}
        ]
        
        iac_array = [
            {"id": "sg-1", "name": "web-sg", "ports": [80, 443, 8080]},
            {"id": "sg-3", "name": "api-sg", "ports": [3000]}
        ]
        
        changes = self.converter.compare_arrays_with_id_matching(
            cloud_array, iac_array, "security_groups"
        )
        
        # Should have changes for sg-1 (ports difference) and sg-2/sg-3 (added/removed)
        assert len(changes) > 0
        
        # Check for sg-1 ports change
        sg1_changes = [change for change in changes if "sg-1" in change["KeyName"]]
        assert len(sg1_changes) > 0
    
    def test_compare_arrays_without_id_matching(self):
        """Test array comparison without ID matching (primitive arrays)"""
        cloud_array = ["item1", "item2", "item3"]
        iac_array = ["item1", "item2"]
        
        changes = self.converter.compare_arrays_with_id_matching(
            cloud_array, iac_array, "simple_array"
        )
        
        # Should report as full array difference
        assert len(changes) == 1
        assert changes[0]["KeyName"] == "simple_array"
        assert changes[0]["CloudValue"] == cloud_array
        assert changes[0]["IacValue"] == iac_array
    
    def test_path_conversion(self):
        """Test path conversion to dot notation"""
        test_cases = [
            ("root['tags']['totalAmount']", "tags.totalAmount"),
            ("root['config']['instance_type']", "config.instance_type"),
            ("root['security_groups'][0]", "security_groups.0"),
            ("root['nested']['deep']['property']", "nested.deep.property")
        ]
        
        for input_path, expected in test_cases:
            result = self.converter._convert_path_to_key_name(input_path)
            assert result == expected
