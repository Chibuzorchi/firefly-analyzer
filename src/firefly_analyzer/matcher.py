"""
Resource matching heuristics for cloud and IaC resources
"""

from typing import Any, Dict, List, Optional, Tuple
from .utils import normalize_value


class ResourceMatcher:
    """
    Handles matching of cloud resources with IaC resources using multiple heuristics.
    
    Matching order:
    1. Primary: exact match on id, resource_id, or arn
    2. Secondary: exact match on (type/resourceType, name) tuple
    3. Tertiary: fallback match on name and region
    """
    
    def __init__(self):
        self.match_cache = {}
    
    def find_matching_iac_resource(self, cloud_resource: Dict[str, Any], 
                                 iac_resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the best matching IaC resource for a given cloud resource.
        
        Args:
            cloud_resource: The cloud resource to match
            iac_resources: List of available IaC resources
            
        Returns:
            The best matching IaC resource or None if no match found
        """
        # Primary matching: exact ID match
        primary_match = self._primary_match(cloud_resource, iac_resources)
        if primary_match:
            return primary_match
        
        # Secondary matching: type and name tuple
        secondary_match = self._secondary_match(cloud_resource, iac_resources)
        if secondary_match:
            return secondary_match
        
        # Tertiary matching: name and region fallback
        tertiary_match = self._tertiary_match(cloud_resource, iac_resources)
        if tertiary_match:
            return tertiary_match
        
        return None
    
    def _primary_match(self, cloud_resource: Dict[str, Any], 
                      iac_resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Primary matching: exact match on id, resource_id, or arn.
        """
        cloud_id_fields = ['id', 'resource_id', 'arn']
        cloud_ids = [cloud_resource.get(field) for field in cloud_id_fields if cloud_resource.get(field)]
        
        for iac_resource in iac_resources:
            for field in cloud_id_fields:
                if field in iac_resource and iac_resource[field] in cloud_ids:
                    return iac_resource
        
        return None
    
    def _secondary_match(self, cloud_resource: Dict[str, Any], 
                        iac_resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Secondary matching: exact match on (type/resourceType, name) tuple.
        """
        cloud_type = cloud_resource.get('type') or cloud_resource.get('resourceType')
        cloud_name = cloud_resource.get('name')
        
        if not cloud_type or not cloud_name:
            return None
        
        for iac_resource in iac_resources:
            iac_type = iac_resource.get('type') or iac_resource.get('resourceType')
            iac_name = iac_resource.get('name')
            
            if (iac_type == cloud_type and 
                iac_name == cloud_name):
                return iac_resource
        
        return None
    
    def _tertiary_match(self, cloud_resource: Dict[str, Any], 
                       iac_resources: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Tertiary matching: fallback match on name and region.
        """
        cloud_name = cloud_resource.get('name')
        cloud_region = cloud_resource.get('region')
        
        if not cloud_name:
            return None
        
        # First try with region match
        if cloud_region:
            for iac_resource in iac_resources:
                iac_name = iac_resource.get('name')
                iac_region = iac_resource.get('region')
                
                if (iac_name == cloud_name and 
                    iac_region == cloud_region):
                    return iac_resource
        
        # Fallback to name-only match
        for iac_resource in iac_resources:
            iac_name = iac_resource.get('name')
            if iac_name == cloud_name:
                return iac_resource
        
        return None
    
    def get_match_confidence(self, cloud_resource: Dict[str, Any], 
                           iac_resource: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a match (0.0 to 1.0).
        
        Args:
            cloud_resource: The cloud resource
            iac_resource: The matched IaC resource
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # ID match (highest confidence)
        cloud_id_fields = ['id', 'resource_id', 'arn']
        iac_id_fields = ['id', 'resource_id', 'arn']
        
        for cloud_field in cloud_id_fields:
            for iac_field in iac_id_fields:
                if (cloud_resource.get(cloud_field) and 
                    iac_resource.get(iac_field) and
                    cloud_resource[cloud_field] == iac_resource[iac_field]):
                    return 1.0
        
        # Type and name match
        cloud_type = cloud_resource.get('type') or cloud_resource.get('resourceType')
        iac_type = iac_resource.get('type') or iac_resource.get('resourceType')
        cloud_name = cloud_resource.get('name')
        iac_name = iac_resource.get('name')
        
        if cloud_type == iac_type:
            score += 0.4
        if cloud_name == iac_name:
            score += 0.4
        
        # Region match
        cloud_region = cloud_resource.get('region')
        iac_region = iac_resource.get('region')
        
        if cloud_region == iac_region:
            score += 0.2
        
        return min(score, 1.0)
