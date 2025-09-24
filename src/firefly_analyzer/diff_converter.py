"""
Convert deepdiff results to the required ChangeLog format
"""

from typing import Any, Dict, List, Union
from deepdiff import DeepDiff
from .utils import get_nested_value, normalize_value


class DiffConverter:
    """
    Converts deepdiff results to the required ChangeLog format.
    """

    def __init__(self):
        self.change_log = []

    def convert_diff_to_changelog(
        self, cloud_resource: Dict[str, Any], iac_resource: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert deepdiff results to ChangeLog format.

        Args:
            cloud_resource: The cloud resource
            iac_resource: The IaC resource

        Returns:
            List of changes in the required format
        """
        self.change_log = []

        # Perform deep diff
        diff = DeepDiff(
            iac_resource,
            cloud_resource,
            ignore_order=True,
            exclude_paths=["root['id']", "root['resource_id']", "root['arn']"],
        )

        if not diff:
            return []

        # Process different types of changes
        self._process_values_changed(diff.get("values_changed", {}))
        self._process_dictionary_item_added(diff.get("dictionary_item_added", []))
        self._process_dictionary_item_removed(diff.get("dictionary_item_removed", []))
        self._process_type_changes(diff.get("type_changes", {}))
        self._process_iterable_item_added(diff.get("iterable_item_added", {}))
        self._process_iterable_item_removed(diff.get("iterable_item_removed", {}))

        return self.change_log

    def _process_values_changed(self, values_changed: Dict[str, Any]) -> None:
        """Process values_changed from deepdiff."""
        for path, change in values_changed.items():
            key_name = self._convert_path_to_key_name(path)
            cloud_value = change.get("new_value")
            iac_value = change.get("old_value")

            # Normalize values for comparison
            cloud_value = normalize_value(cloud_value)
            iac_value = normalize_value(iac_value)

            self.change_log.append(
                {"KeyName": key_name, "CloudValue": cloud_value, "IacValue": iac_value}
            )

    def _process_dictionary_item_added(self, items_added: List[str]) -> None:
        """Process dictionary_item_added from deepdiff."""
        for path in items_added:
            key_name = self._convert_path_to_key_name(path)
            # For added items, IaC value is None/empty
            self.change_log.append(
                {"KeyName": key_name, "CloudValue": "ADDED", "IacValue": None}
            )

    def _process_dictionary_item_removed(self, items_removed: List[str]) -> None:
        """Process dictionary_item_removed from deepdiff."""
        for path in items_removed:
            key_name = self._convert_path_to_key_name(path)
            # For removed items, Cloud value is None/empty
            self.change_log.append(
                {"KeyName": key_name, "CloudValue": None, "IacValue": "REMOVED"}
            )

    def _process_type_changes(self, type_changes: Dict[str, Any]) -> None:
        """Process type_changes from deepdiff."""
        for path, change in type_changes.items():
            key_name = self._convert_path_to_key_name(path)
            cloud_value = change.get("new_value")
            iac_value = change.get("old_value")

            self.change_log.append(
                {
                    "KeyName": key_name,
                    "CloudValue": f"{type(cloud_value).__name__}: {cloud_value}",
                    "IacValue": f"{type(iac_value).__name__}: {iac_value}",
                }
            )

    def _process_iterable_item_added(self, items_added: Dict[str, Any]) -> None:
        """Process iterable_item_added from deepdiff."""
        for path, items in items_added.items():
            key_name = self._convert_path_to_key_name(path)
            for item in items:
                self.change_log.append(
                    {"KeyName": f"{key_name}[+]", "CloudValue": item, "IacValue": None}
                )

    def _process_iterable_item_removed(self, items_removed: Dict[str, Any]) -> None:
        """Process iterable_item_removed from deepdiff."""
        for path, items in items_removed.items():
            key_name = self._convert_path_to_key_name(path)
            for item in items:
                self.change_log.append(
                    {"KeyName": f"{key_name}[-]", "CloudValue": None, "IacValue": item}
                )

    def _convert_path_to_key_name(self, path: str) -> str:
        """
        Convert deepdiff path to dot notation key name.

        Args:
            path: DeepDiff path (e.g., "root['tags']['totalAmount']")

        Returns:
            Dot notation key name (e.g., "tags.totalAmount")
        """
        # Remove 'root' prefix and convert to dot notation
        if path.startswith("root['"):
            path = path[6:]  # Remove "root['"
        if path.endswith("']"):
            path = path[:-2]  # Remove "']"

        # Replace "']['" with "."
        path = path.replace("']['", ".")

        # Handle array indices - convert "][0]" to ".0"
        path = path.replace("][", ".")

        # Clean up any remaining brackets
        path = path.replace("'", "").replace("[", "").replace("]", "")

        return path

    def compare_arrays_with_id_matching(
        self, cloud_array: List[Any], iac_array: List[Any], array_path: str
    ) -> List[Dict[str, Any]]:
        """
        Compare arrays by matching elements with 'id' fields.

        Args:
            cloud_array: Cloud resource array
            iac_array: IaC resource array
            array_path: Path to the array in dot notation

        Returns:
            List of changes found in the arrays
        """
        changes = []

        # Create lookup maps for arrays with id fields
        cloud_map = {}
        iac_map = {}

        # Check if arrays contain objects with id fields
        if (
            cloud_array
            and isinstance(cloud_array[0], dict)
            and iac_array
            and isinstance(iac_array[0], dict)
        ):

            # Build maps using id field
            for item in cloud_array:
                if "id" in item:
                    cloud_map[item["id"]] = item

            for item in iac_array:
                if "id" in item:
                    iac_map[item["id"]] = item

            # Compare matched items
            all_ids = set(cloud_map.keys()) | set(iac_map.keys())
            for item_id in all_ids:
                cloud_item = cloud_map.get(item_id)
                iac_item = iac_map.get(item_id)

                if cloud_item and iac_item:
                    # Both exist, compare them
                    item_diff = DeepDiff(iac_item, cloud_item, ignore_order=True)
                    if item_diff:
                        for change_type, changes_dict in item_diff.items():
                            if isinstance(changes_dict, dict):
                                for path, change in changes_dict.items():
                                    key_name = f"{array_path}.{item_id}.{self._convert_path_to_key_name(path)}"
                                    if isinstance(change, dict):
                                        changes.append(
                                            {
                                                "KeyName": key_name,
                                                "CloudValue": change.get(
                                                    "new_value", change
                                                ),
                                                "IacValue": change.get(
                                                    "old_value", change
                                                ),
                                            }
                                        )
                                    else:
                                        changes.append(
                                            {
                                                "KeyName": key_name,
                                                "CloudValue": change,
                                                "IacValue": change,
                                            }
                                        )
                elif cloud_item:
                    # Only in cloud
                    changes.append(
                        {
                            "KeyName": f"{array_path}.{item_id}",
                            "CloudValue": "ADDED",
                            "IacValue": None,
                        }
                    )
                elif iac_item:
                    # Only in IaC
                    changes.append(
                        {
                            "KeyName": f"{array_path}.{item_id}",
                            "CloudValue": None,
                            "IacValue": "REMOVED",
                        }
                    )
        else:
            # Arrays don't have id fields, report as full array difference
            changes.append(
                {
                    "KeyName": array_path,
                    "CloudValue": cloud_array,
                    "IacValue": iac_array,
                }
            )

        return changes
