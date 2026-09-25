"""
s3_upload.py
-------------
Phase 3 — AWS S3 Upload Script

This script uploads all project data files to your AWS S3 bucket
using the boto3 library (AWS SDK for Python).

HOW TO USE:
1. Install boto3:       pip install boto3 python-dotenv
2. Create a .env file in the project root with your credentials (see below)
3. Run this script:    python aws/s3_upload.py

.env file format (create this file, NEVER commit it to GitHub):
--------------------------------------------------------------
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=ecommerce-analytics-yourname
--------------------------------------------------------------
"""

import boto3
import os
import sys
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

# ─────────────────────────────────────────────────────────
# Try to load credentials from .env file
# ─────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    # Look for .env in the project root (one level up from aws/)
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    print("✓ Loaded credentials from .env file")
except ImportError:
    print("⚠ python-dotenv not installed. Reading from system environment variables.")
    print("  Install with: pip install python-dotenv")

# ─────────────────────────────────────────────────────────
# Configuration — reads from .env or environment variables
# ─────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "ap-south-1")
BUCKET_NAME           = os.getenv("S3_BUCKET_NAME")

# Validate credentials exist
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not BUCKET_NAME:
    print("\n❌ ERROR: Missing AWS credentials or bucket name.")
    print("   Please create a .env file in the project root with:")
    print("   AWS_ACCESS_KEY_ID=your_key")
    print("   AWS_SECRET_ACCESS_KEY=your_secret")
    print("   S3_BUCKET_NAME=your-bucket-name")
    sys.exit(1)

# ─────────────────────────────────────────────────────────
# Define files to upload
# ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent

# Files mapped to their S3 destination paths
FILES_TO_UPLOAD = {
    # Local path (relative to project root)  →  S3 key (folder/filename)
    "data/raw/regions.csv":         "raw/regions.csv",
    "data/raw/products.csv":        "raw/products.csv",
    "data/raw/customers.csv":       "raw/customers.csv",
    "data/raw/orders.csv":          "raw/orders.csv",
    "data/raw/order_details.csv":   "raw/order_details.csv",
    "data/raw/ecommerce_flat.csv":  "raw/ecommerce_flat.csv",
    "data/data_dictionary.md":      "raw/data_dictionary.md",
    "excel/ecommerce_analysis.xlsx":"raw/ecommerce_analysis.xlsx",
}

# ─────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────

def get_file_size_mb(filepath):
    """Returns file size in MB."""
    size_bytes = os.path.getsize(filepath)
    return round(size_bytes / (1024 * 1024), 2)


def bucket_exists(s3_client, bucket_name):
    """Check if the S3 bucket exists and is accessible."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            print(f"❌ Bucket '{bucket_name}' does not exist.")
        elif error_code == "403":
            print(f"❌ Access denied to bucket '{bucket_name}'. Check IAM permissions.")
        else:
            print(f"❌ Error checking bucket: {e}")
        return False


def upload_file(s3_client, local_path, bucket_name, s3_key):
    """
    Upload a single file to S3.

    local_path  : full local file path
    bucket_name : S3 bucket name
    s3_key      : destination path inside the bucket (e.g., 'raw/orders.csv')
    """
    try:
        file_size = get_file_size_mb(local_path)
        print(f"  Uploading: {os.path.basename(local_path):<30} ({file_size} MB) → s3://{bucket_name}/{s3_key}")

        s3_client.upload_file(
            Filename=str(local_path),
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={
                "ServerSideEncryption": "AES256",  # Encrypt at rest
                "Metadata": {
                    "project": "ecommerce-analytics",
                    "phase": "raw-data",
                }
            }
        )
        return True

    except FileNotFoundError:
        print(f"  ⚠ File not found: {local_path} — skipping")
        return False
    except ClientError as e:
        print(f"  ❌ Upload failed for {local_path}: {e}")
        return False


def upload_cleaned_data(s3_client, bucket_name):
    """
    Upload cleaned data to the 'cleaned/' folder.
    This is called after Phase 4 (Python cleaning) is complete.
    """
    cleaned_file = BASE_DIR / "data" / "cleaned" / "ecommerce_cleaned.csv"
    if cleaned_file.exists():
        upload_file(s3_client, str(cleaned_file), bucket_name, "cleaned/ecommerce_cleaned.csv")
    else:
        print("  ℹ cleaned/ecommerce_cleaned.csv not found yet — run Phase 4 first.")


# ─────────────────────────────────────────────────────────
# MAIN UPLOAD PROCESS
# ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  E-Commerce Analytics — AWS S3 Upload")
    print("=" * 60)
    print(f"\n  Bucket : {BUCKET_NAME}")
    print(f"  Region : {AWS_REGION}")
    print()

    # Create S3 client
    try:
        s3_client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    except Exception as e:
        print(f"❌ Failed to create S3 client: {e}")
        sys.exit(1)

    # Verify bucket exists
    if not bucket_exists(s3_client, BUCKET_NAME):
        print("\n  To create the bucket, follow the guide in aws/aws_setup.md")
        sys.exit(1)

    print("✓ Bucket found and accessible\n")
    print("Uploading raw data files:")
    print("-" * 60)

    success_count = 0
    fail_count    = 0

    for local_rel_path, s3_key in FILES_TO_UPLOAD.items():
        local_full_path = BASE_DIR / local_rel_path
        if upload_file(s3_client, str(local_full_path), BUCKET_NAME, s3_key):
            success_count += 1
        else:
            fail_count += 1

    # Also try to upload cleaned data if it exists
    print("\nChecking for cleaned data:")
    print("-" * 60)
    upload_cleaned_data(s3_client, BUCKET_NAME)

    # Summary
    print("\n" + "=" * 60)
    print(f"  Upload Complete")
    print("=" * 60)
    print(f"  ✓ Successful : {success_count}")
    print(f"  ✗ Failed     : {fail_count}")
    print(f"\n  View files at:")
    print(f"  https://s3.console.aws.amazon.com/s3/buckets/{BUCKET_NAME}")
    print()


if __name__ == "__main__":
    main()
