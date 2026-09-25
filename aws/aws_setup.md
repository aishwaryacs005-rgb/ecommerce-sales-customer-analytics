# AWS S3 Setup Guide — E-Commerce Analytics Project

## What is AWS S3?

Amazon S3 (Simple Storage Service) is a cloud storage service.  
Think of it as Google Drive, but designed specifically for storing data files that  
programs and analytics tools can access directly.

In a real Data Analyst job, raw data files are almost never stored on your laptop.  
They are stored on a cloud platform like AWS S3 so that:
- Multiple team members can access the same data
- Data is backed up automatically
- Analytics tools (Python, SQL engines, BI tools) can read data directly from the cloud
- There is a clear separation between raw data, cleaned data, and processed outputs

---

## S3 Folder Structure for This Project

```
ecommerce-analytics/                    ← S3 Bucket (top level)
│
├── raw/                                ← Original, untouched files
│   ├── regions.csv
│   ├── products.csv
│   ├── customers.csv
│   ├── orders.csv
│   ├── order_details.csv
│   └── ecommerce_flat.csv
│
├── cleaned/                            ← After Python cleaning (Phase 4)
│   └── ecommerce_cleaned.csv
│
└── processed/                          ← Final outputs, exports
    └── ecommerce_for_powerbi.csv
```

**Why these 3 folders?**

| Folder    | Purpose                                                                 |
|-----------|-------------------------------------------------------------------------|
| raw/      | Never modify files here. This is your source of truth.                  |
| cleaned/  | Store cleaned data here after Python processing.                        |
| processed/| Final outputs ready for Power BI, SQL, or reporting.                    |

This is called a **Data Lake pattern** — a standard structure used in real companies.

---

## Step-by-Step: Create an AWS Account

If you do not have an AWS account:

1. Go to: https://aws.amazon.com
2. Click **"Create an AWS Account"**
3. Enter your email address and choose a password
4. Account type: select **Personal**
5. Enter your contact information
6. Enter a credit/debit card (AWS Free Tier is free for 12 months — S3 is included)
7. Verify your phone number
8. Select **Basic Support Plan (Free)**
9. Click **Complete Sign Up**

> **Important:** AWS Free Tier gives you 5 GB of S3 storage free for 12 months.  
> This project's files are under 50 MB total — well within the free tier.

---

## Step-by-Step: Create an S3 Bucket

1. Log in to AWS Console: https://console.aws.amazon.com
2. In the search bar at the top, type **S3** and click it
3. Click the orange **"Create bucket"** button
4. Fill in the details:

   | Field                       | Value                                    |
   |-----------------------------|------------------------------------------|
   | Bucket name                 | `ecommerce-analytics-yourname`           |
   | AWS Region                  | `ap-south-1` (Asia Pacific - Mumbai)     |
   | Block all public access     | ✅ Keep checked (NEVER make data public) |
   | Bucket Versioning           | Disable (not needed for this project)    |
   | Default encryption          | Enable (SSE-S3)                          |

   > **Bucket naming rules:** All lowercase, no spaces, no underscores, hyphens are OK.  
   > Bucket names must be globally unique — add your name to make it unique.

5. Leave all other settings as default
6. Click **"Create bucket"** at the bottom

Your bucket is created. You will see it in the S3 console.

---

## Step-by-Step: Create Folders Inside the Bucket

1. Click on your bucket name to open it
2. Click **"Create folder"**
3. Folder name: `raw`
4. Server-side encryption: SSE-S3
5. Click **"Create folder"**
6. Repeat to create: `cleaned` and `processed`

You now have 3 folders inside your bucket.

---

## Step-by-Step: Manually Upload Files (AWS Console)

1. Click on the `raw/` folder to open it
2. Click **"Upload"**
3. Click **"Add files"**
4. Navigate to your project folder: `data/raw/`
5. Select all 6 CSV files:
   - `regions.csv`
   - `products.csv`
   - `customers.csv`
   - `orders.csv`
   - `order_details.csv`
   - `ecommerce_flat.csv`
6. Click **"Upload"**
7. Wait for the green success message

---

## Step-by-Step: Create an IAM User for Programmatic Access

To use Python (boto3) to upload files, you need an **Access Key**.  
Never use your root AWS account for programmatic access — create an IAM user instead.

1. In AWS Console search bar, type **IAM** and click it
2. Click **"Users"** in the left sidebar
3. Click **"Create user"**
4. User name: `ecommerce-analytics-user`
5. Click **Next**
6. Permissions: click **"Attach policies directly"**
7. Search for `AmazonS3FullAccess` and check it
8. Click **Next** → **Create user**
9. Click on the newly created user
10. Click the **"Security credentials"** tab
11. Scroll to **"Access keys"** → Click **"Create access key"**
12. Use case: select **"Local code"**
13. Click **Next** → **Create access key**
14. **IMPORTANT:** Download the CSV file or copy both keys NOW.  
    You will never see the Secret Access Key again after closing this page.

> **Security rule:** Never commit Access Keys to GitHub. Never share them.  
> Store them in a `.env` file and add `.env` to `.gitignore`.

---

## Security Best Practices for This Project

| Rule                              | Why                                                        |
|-----------------------------------|------------------------------------------------------------|
| Block all public access on bucket | Prevents anyone on the internet from reading your data     |
| Use IAM user, not root account    | Limits damage if credentials are accidentally exposed      |
| Store keys in .env file only      | Keeps secrets out of your code and GitHub                  |
| Add .env to .gitignore            | Prevents accidental key upload to GitHub                   |
| Enable bucket encryption (SSE-S3) | Data is encrypted at rest on AWS servers                   |
| Use ap-south-1 (Mumbai) region    | Lower latency from India, data stays within India          |

---

## S3 Object URL Structure

Every file you upload to S3 gets a URL in this format:

```
https://<bucket-name>.s3.<region>.amazonaws.com/<folder>/<filename>

Example:
https://ecommerce-analytics-yourname.s3.ap-south-1.amazonaws.com/raw/orders.csv
```

Since your bucket is private, this URL requires authentication to access.  
The Python script below handles authentication automatically using your Access Keys.

---

## How Python Reads Data from S3

Once files are uploaded, your Python cleaning script (Phase 4) can read them directly:

```python
import boto3
import pandas as pd
from io import StringIO

# Connect to S3
s3 = boto3.client("s3",
    region_name="ap-south-1",
    aws_access_key_id="YOUR_ACCESS_KEY",
    aws_secret_access_key="YOUR_SECRET_KEY"
)

# Read a CSV from S3 directly into a Pandas DataFrame
bucket = "ecommerce-analytics-yourname"
obj = s3.get_object(Bucket=bucket, Key="raw/orders.csv")
df = pd.read_csv(StringIO(obj["Body"].read().decode("utf-8")))

print(df.shape)
```

This is how real data pipelines work — Python pulls data from S3, cleans it,  
and uploads the cleaned version back to S3.

---

## Cost Estimate for This Project

| Service     | Usage               | Cost (Free Tier)         |
|-------------|---------------------|--------------------------|
| S3 Storage  | ~50 MB of CSV files | Free (up to 5 GB/month)  |
| S3 Requests | ~100 PUT/GET calls  | Free (up to 20,000/month)|
| Data Transfer| Within AWS region  | Free                     |

**Total expected cost: ₹0** — well within AWS Free Tier limits.

---

*Document created as part of Phase 3 — AWS S3 Setup*  
*Project: E-Commerce Sales & Customer Analytics*
