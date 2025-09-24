"""
S3 uploader for LocalStack integration
"""

import json
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Uploader:
    """
    Handles uploading analysis reports to S3 (including LocalStack).
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
    ):
        """
        Initialize S3 uploader.

        Args:
            endpoint_url: S3 endpoint URL (for LocalStack)
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
        """
        self.endpoint_url = endpoint_url
        self.region_name = region_name

        # Initialize S3 client
        if aws_access_key_id and aws_secret_access_key:
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )
        else:
            # Use default AWS credentials (from environment or IAM role)
            session = boto3.Session(region_name=region_name)

        if endpoint_url:
            self.s3_client = session.client("s3", endpoint_url=endpoint_url)
        else:
            self.s3_client = session.client("s3")

    def upload_report(self, report_data: dict, bucket_name: str, key: str) -> bool:
        """
        Upload analysis report to S3.

        Args:
            report_data: The analysis report data
            bucket_name: S3 bucket name
            key: S3 object key

        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Convert report to JSON string
            report_json = json.dumps(report_data, indent=2, ensure_ascii=False)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=report_json.encode("utf-8"),
                ContentType="application/json",
            )

            return True

        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False
        except NoCredentialsError:
            print("Error: AWS credentials not found")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """
        Create S3 bucket if it doesn't exist.

        Args:
            bucket_name: Name of the bucket to create

        Returns:
            True if bucket exists or was created successfully, False otherwise
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Bucket doesn't exist, create it
                try:
                    if self.endpoint_url:
                        # For LocalStack, we don't need to specify location
                        self.s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        # For real AWS, specify location constraint
                        self.s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={
                                "LocationConstraint": self.region_name
                            },
                        )
                    return True
                except ClientError as create_error:
                    print(f"Error creating bucket: {create_error}")
                    return False
            else:
                print(f"Error checking bucket: {e}")
                return False

    def list_buckets(self) -> list:
        """
        List all available buckets.

        Returns:
            List of bucket names
        """
        try:
            response = self.s3_client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []

    def download_report(self, bucket_name: str, key: str) -> Optional[dict]:
        """
        Download analysis report from S3.

        Args:
            bucket_name: S3 bucket name
            key: S3 object key

        Returns:
            Downloaded report data or None if failed
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            report_json = response["Body"].read().decode("utf-8")
            return json.loads(report_json)
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
