"""
Command-line interface for the Firefly Analyzer
"""

import click
import json
from pathlib import Path
from typing import Optional
from .analyzer import CloudIacAnalyzer
from .s3_uploader import S3Uploader
from .utils import load_json_file, save_json_file


@click.group()
def cli():
    """Firefly Asset Management Solution - Cloud to IaC Resources Analyzer"""
    pass


@cli.command()
@click.option('--cloud', '-c', required=True, type=click.Path(exists=True),
              help='Path to cloud resources JSON file')
@click.option('--iac', '-i', required=True, type=click.Path(exists=True),
              help='Path to IaC resources JSON file')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path for analysis report')
@click.option('--upload-s3', 'bucket_name', 
              help='S3 bucket name to upload report')
@click.option('--s3-key', 's3_key',
              help='S3 object key for the report')
@click.option('--localstack-endpoint', 'endpoint_url',
              help='LocalStack S3 endpoint URL')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def analyze(cloud: str, iac: str, output: Optional[str], 
           bucket_name: Optional[str], s3_key: Optional[str],
           endpoint_url: Optional[str], verbose: bool):
    """
    Analyze cloud resources against IaC resources.
    
    This command compares cloud resources with their corresponding
    Infrastructure-as-Code definitions and generates a detailed report.
    """
    try:
        if verbose:
            click.echo("🔍 Starting Firefly Analysis...")
            click.echo(f"📁 Cloud resources: {cloud}")
            click.echo(f"📁 IaC resources: {iac}")
        
        # Initialize analyzer
        analyzer = CloudIacAnalyzer()
        
        # Perform analysis
        if verbose:
            click.echo("⚙️  Loading resources...")
        
        analysis_report = analyzer.analyze_from_files(cloud, iac, output)
        
        if verbose:
            click.echo("✅ Analysis completed!")
            click.echo(f"📊 Summary: {analysis_report['summary']}")
        
        # Display summary
        summary = analysis_report['summary']
        click.echo("\n📈 ANALYSIS SUMMARY")
        click.echo("=" * 50)
        click.echo(f"Total Resources: {summary['total']}")
        click.echo(f"✅ Matched: {summary['match']}")
        click.echo(f"⚠️  Modified: {summary['modified']}")
        click.echo(f"❌ Missing: {summary['missing']}")
        
        # Show detailed changes if any
        if summary['modified'] > 0:
            click.echo("\n🔍 DETAILED CHANGES")
            click.echo("=" * 50)
            detailed_changes = analyzer.get_detailed_changes(analysis_report['analysis'])
            for change_info in detailed_changes:
                click.echo(f"\nResource: {change_info['resource_name']} ({change_info['resource_id']})")
                change = change_info['change']
                click.echo(f"  • {change['KeyName']}: '{change['IacValue']}' → '{change['CloudValue']}'")
        
        # Upload to S3 if requested
        if bucket_name:
            if verbose:
                click.echo(f"\n☁️  Uploading to S3 bucket: {bucket_name}")
            
            uploader = S3Uploader(endpoint_url=endpoint_url)
            
            # Create bucket if it doesn't exist
            if not uploader.create_bucket_if_not_exists(bucket_name):
                click.echo("❌ Failed to create/access S3 bucket")
                return
            
            # Generate S3 key if not provided
            if not s3_key:
                timestamp = Path(cloud).stem
                s3_key = f"firefly-analysis-{timestamp}.json"
            
            # Upload report
            if uploader.upload_report(analysis_report, bucket_name, s3_key):
                click.echo(f"✅ Report uploaded to s3://{bucket_name}/{s3_key}")
            else:
                click.echo("❌ Failed to upload report to S3")
        
        # Save to local file if output specified
        if output:
            click.echo(f"💾 Report saved to: {output}")
        
        if verbose:
            click.echo("\n🎉 Analysis complete!")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--bucket', '-b', required=True,
              help='S3 bucket name')
@click.option('--key', '-k', required=True,
              help='S3 object key')
@click.option('--localstack-endpoint', 'endpoint_url',
              help='LocalStack S3 endpoint URL')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path for downloaded report')
def download(bucket: str, key: str, endpoint_url: Optional[str], 
            output: Optional[str]):
    """
    Download analysis report from S3.
    """
    try:
        click.echo(f"📥 Downloading report from s3://{bucket}/{key}")
        
        uploader = S3Uploader(endpoint_url=endpoint_url)
        report = uploader.download_report(bucket, key)
        
        if report:
            if output:
                save_json_file(report, output)
                click.echo(f"✅ Report saved to: {output}")
            else:
                click.echo(json.dumps(report, indent=2))
        else:
            click.echo("❌ Failed to download report")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--localstack-endpoint', 'endpoint_url',
              help='LocalStack S3 endpoint URL')
def list_buckets(endpoint_url: Optional[str]):
    """
    List available S3 buckets.
    """
    try:
        uploader = S3Uploader(endpoint_url=endpoint_url)
        buckets = uploader.list_buckets()
        
        if buckets:
            click.echo("📦 Available S3 buckets:")
            for bucket in buckets:
                click.echo(f"  • {bucket}")
        else:
            click.echo("No buckets found")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
