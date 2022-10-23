# AWS S3 Delete Python example

This folder contains a Python application example that handles S3 buckets on AWS (Amazon Web Services).

Delete a S3 bucket using the Client API (low-level) of Boto 3.

## Requirements

* You must have an [Amazon Web Services (AWS)](http://aws.amazon.com/) account.

* The code was written for:
  
  * Python 3
  * AWS SDK for Python (Boto3)

* This example uses Client API (low-level) of Boto 3.

* Install the AWS SDK for Python (Boto3).

  Install the latest Boto 3 release via pip:

  ```bash
  pip install boto3
  ```

## Using the code

* Configure your AWS access keys.

  Run application:

  ```bash
  python s3delete.py <BUCKET_NAME>
  ```

* Test the application.

  You should not see the S3 bucket deleted.
