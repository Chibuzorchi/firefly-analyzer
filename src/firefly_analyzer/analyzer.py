"""
Main analyzer orchestration for cloud to IaC resource comparison
"""

from typing import Any, Dict, List, Optional
from .matcher import ResourceMatcher
from .diff_converter import DiffConverter
from .utils import load_json_file, save_json_file


class CloudIacAnalyzer:
    """
    Main analyzer class that orchestrates the comparison of cloud resources
    with their corresponding IaC definitions.
    """
    
    def __init__(self):
        self.matcher = ResourceMatcher()
        self.diff_converter = DiffConverter()
    
    def analyze(self, cloud_resources: List[Dict[str, Any]], 
                iac_resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze cloud resources against IaC resources.
        
        Args:
            cloud_resources: List of cloud resources
            iac_resources: List of IaC resources
            
        Returns:
            Analysis report with summary and detailed results
        """
        analysis_results = []
        
        for cloud_resource in cloud_resources:
            analysis_item = self._analyze_single_resource(cloud_resource, iac_resources)
            analysis_results.append(analysis_item)
        
        # Generate summary
        summary = self._generate_summary(analysis_results)
        
        return {
            "analysis": analysis_results,
            "summary": summary
        }
    
    def _analyze_single_resource(self, cloud_resource: Dict[str, Any], 
                                iac_resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a single cloud resource against IaC resources.
        
        Args:
            cloud_resource: The cloud resource to analyze
            iac_resources: List of available IaC resources
            
        Returns:
            Analysis result for the single resource
        """
        # Find matching IaC resource
        matching_iac = self.matcher.find_matching_iac_resource(cloud_resource, iac_resources)
        
        if not matching_iac:
            return {
                "CloudResourceItem": cloud_resource,
                "IacResourceItem": None,
                "State": "Missing",
                "ChangeLog": []
            }
        
        # Check if resources are identical
        if self._are_resources_identical(cloud_resource, matching_iac):
            return {
                "CloudResourceItem": cloud_resource,
                "IacResourceItem": matching_iac,
                "State": "Match",
                "ChangeLog": []
            }
        
        # Resources differ, generate change log
        change_log = self.diff_converter.convert_diff_to_changelog(
            cloud_resource, matching_iac
        )
        
        return {
            "CloudResourceItem": cloud_resource,
            "IacResourceItem": matching_iac,
            "State": "Modified",
            "ChangeLog": change_log
        }
    
    def _are_resources_identical(self, cloud_resource: Dict[str, Any], 
                                iac_resource: Dict[str, Any]) -> bool:
        """
        Check if two resources are identical (ignoring ID fields).
        
        Args:
            cloud_resource: Cloud resource
            iac_resource: IaC resource
            
        Returns:
            True if resources are identical, False otherwise
        """
        from deepdiff import DeepDiff
        
        # Create copies without ID fields for comparison
        cloud_copy = {k: v for k, v in cloud_resource.items() 
                     if k not in ['id', 'resource_id', 'arn']}
        iac_copy = {k: v for k, v in iac_resource.items() 
                   if k not in ['id', 'resource_id', 'arn']}
        
        diff = DeepDiff(iac_copy, cloud_copy, ignore_order=True)
        return not diff
    
    def _generate_summary(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Generate summary statistics from analysis results.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Summary statistics
        """
        total = len(analysis_results)
        missing = sum(1 for result in analysis_results if result["State"] == "Missing")
        modified = sum(1 for result in analysis_results if result["State"] == "Modified")
        match = sum(1 for result in analysis_results if result["State"] == "Match")
        
        return {
            "total": total,
            "missing": missing,
            "modified": modified,
            "match": match
        }
    
    def analyze_from_files(self, cloud_file: str, iac_file: str, 
                          output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze resources from JSON files.
        
        Args:
            cloud_file: Path to cloud resources JSON file
            iac_file: Path to IaC resources JSON file
            output_file: Optional path to save the analysis report
            
        Returns:
            Analysis report
        """
        # Load resources from files
        cloud_resources = load_json_file(cloud_file)
        iac_resources = load_json_file(iac_file)
        
        # Ensure we have lists
        if not isinstance(cloud_resources, list):
            cloud_resources = [cloud_resources]
        if not isinstance(iac_resources, list):
            iac_resources = [iac_resources]
        
        # Perform analysis
        analysis_report = self.analyze(cloud_resources, iac_resources)
        
        # Save to output file if specified
        if output_file:
            save_json_file(analysis_report, output_file)
        
        return analysis_report
    
    def get_detailed_changes(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get detailed information about all changes found.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            List of detailed change information
        """
        detailed_changes = []
        
        for result in analysis_results:
            if result["State"] == "Modified" and result["ChangeLog"]:
                for change in result["ChangeLog"]:
                    detailed_changes.append({
                        "resource_id": result["CloudResourceItem"].get("id", "unknown"),
                        "resource_name": result["CloudResourceItem"].get("name", "unknown"),
                        "change": change
                    })
        
        return detailed_changes
