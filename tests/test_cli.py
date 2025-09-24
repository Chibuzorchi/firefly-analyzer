"""
Tests for the CLI interface
"""

import pytest
import json
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from firefly_analyzer.cli import cli


class TestCLI:
    """Test CLI functionality"""

    def test_analyze_command_with_files(self):
        """Test analyze command with sample files"""
        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as cloud_file:
            cloud_data = [
                {
                    "id": "ec2-1",
                    "type": "aws_ec2_instance",
                    "name": "web-server",
                    "tags": {"totalAmount": "17kb"},
                }
            ]
            json.dump(cloud_data, cloud_file)
            cloud_path = cloud_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as iac_file:
            iac_data = [
                {
                    "id": "ec2-1",
                    "type": "aws_ec2_instance",
                    "name": "web-server",
                    "tags": {"totalAmount": "22kb"},
                }
            ]
            json.dump(iac_data, iac_file)
            iac_path = iac_file.name

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as output_file:
            output_path = output_file.name

        try:
            # Run CLI command
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "firefly_analyzer.cli",
                    "analyze",
                    "--cloud",
                    cloud_path,
                    "--iac",
                    iac_path,
                    "--output",
                    output_path,
                    "--verbose",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Analysis completed!" in result.stdout
            assert "Modified: 1" in result.stdout

            # Check output file was created
            assert Path(output_path).exists()

            # Check output file content
            with open(output_path, "r") as f:
                output_data = json.load(f)

            assert "analysis" in output_data
            assert "summary" in output_data
            assert output_data["summary"]["modified"] == 1

        finally:
            # Clean up
            Path(cloud_path).unlink()
            Path(iac_path).unlink()
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_analyze_command_missing_files(self):
        """Test analyze command with missing files"""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "firefly_analyzer.cli",
                "analyze",
                "--cloud",
                "nonexistent.json",
                "--iac",
                "nonexistent.json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "Error" in result.stderr

    def test_analyze_command_with_s3_upload(self):
        """Test analyze command with S3 upload (mocked)"""
        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as cloud_file:
            cloud_data = [{"id": "test-1", "name": "test-resource"}]
            json.dump(cloud_data, cloud_file)
            cloud_path = cloud_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as iac_file:
            iac_data = [{"id": "test-1", "name": "test-resource"}]
            json.dump(iac_data, iac_file)
            iac_path = iac_file.name

        try:
            # Mock S3 uploader
            with patch("firefly_analyzer.cli.S3Uploader") as mock_uploader_class:
                mock_uploader = MagicMock()
                mock_uploader.create_bucket_if_not_exists.return_value = True
                mock_uploader.upload_report.return_value = True
                mock_uploader_class.return_value = mock_uploader

                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "firefly_analyzer.cli",
                        "analyze",
                        "--cloud",
                        cloud_path,
                        "--iac",
                        iac_path,
                        "--upload-s3",
                        "test-bucket",
                        "--s3-key",
                        "test-report.json",
                        "--localstack-endpoint",
                        "http://localhost:4566",
                    ],
                    capture_output=True,
                    text=True,
                )

                assert result.returncode == 0
                assert (
                    "Report uploaded to s3://test-bucket/test-report.json"
                    in result.stdout
                )

                # Verify S3 uploader was called
                mock_uploader.create_bucket_if_not_exists.assert_called_once_with(
                    "test-bucket"
                )
                mock_uploader.upload_report.assert_called_once()

        finally:
            # Clean up
            Path(cloud_path).unlink()
            Path(iac_path).unlink()

    def test_download_command(self):
        """Test download command (mocked)"""
        with patch("firefly_analyzer.cli.S3Uploader") as mock_uploader_class:
            mock_uploader = MagicMock()
            mock_uploader.download_report.return_value = {
                "analysis": [],
                "summary": {"total": 0, "match": 0, "modified": 0, "missing": 0},
            }
            mock_uploader_class.return_value = mock_uploader

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "firefly_analyzer.cli",
                    "download",
                    "--bucket",
                    "test-bucket",
                    "--key",
                    "test-report.json",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "summary" in result.stdout

            # Verify S3 uploader was called
            mock_uploader.download_report.assert_called_once_with(
                "test-bucket", "test-report.json"
            )

    def test_list_buckets_command(self):
        """Test list buckets command (mocked)"""
        with patch("firefly_analyzer.cli.S3Uploader") as mock_uploader_class:
            mock_uploader = MagicMock()
            mock_uploader.list_buckets.return_value = ["bucket1", "bucket2", "bucket3"]
            mock_uploader_class.return_value = mock_uploader

            result = subprocess.run(
                [sys.executable, "-m", "firefly_analyzer.cli", "list-buckets"],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "bucket1" in result.stdout
            assert "bucket2" in result.stdout
            assert "bucket3" in result.stdout

            # Verify S3 uploader was called
            mock_uploader.list_buckets.assert_called_once()

    def test_help_command(self):
        """Test help command"""
        result = subprocess.run(
            [sys.executable, "-m", "firefly_analyzer.cli", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Firefly Asset Management Solution" in result.stdout
        assert "analyze" in result.stdout
        assert "download" in result.stdout
        assert "list-buckets" in result.stdout

    def test_analyze_help_command(self):
        """Test analyze command help"""
        result = subprocess.run(
            [sys.executable, "-m", "firefly_analyzer.cli", "analyze", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--cloud" in result.stdout
        assert "--iac" in result.stdout
        assert "--output" in result.stdout
        assert "--upload-s3" in result.stdout
