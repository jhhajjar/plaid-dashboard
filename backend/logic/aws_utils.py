import boto3
import os
import pandas as pd
import json
from logic.transaction_logic import to_file_friendly, custom_serializer
from models.Transaction import TransactionEntity
from dotenv import load_dotenv
from io import StringIO

COLUMNS = [
    "date",
    "authorized_date",
    "transaction_id",
    "name",
    "merchant_name",
    "plaid_categories",
    "amount",
]


def upload_cursor_s3(cursor: str, file_name: str) -> bool:
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # Upload the file
    load_dotenv()
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket = os.getenv("S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        s3_client.put_object(Bucket=bucket, Key=file_name, Body=cursor)
    except Exception as e:
        print(e)
        return False
    return True


def read_cursor_s3(file_name: str) -> str:
    """Read transaction list from an S3 bucket

    :param file_name: File to read
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    load_dotenv()
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket_name = os.getenv("S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        cursor = response["Body"].read().decode("utf-8")
    except Exception as e:
        print(e)
        return ""

    return cursor


def upload_transactions_s3(transactions: TransactionEntity, file_name: str) -> bool:
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    buffer = StringIO()
    json_trs = [to_file_friendly(tr) for tr in transactions]
    json.dump(json_trs, buffer, default=custom_serializer, indent=2)

    # Upload the file
    load_dotenv()
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket = os.getenv("S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        s3_client.put_object(Bucket=bucket, Key=file_name, Body=buffer.getvalue())
    except Exception as e:
        print(e)
        return False
    return True


def read_transactions_s3(file_name):
    """Read transaction list from an S3 bucket

    :param file_name: File to read
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    load_dotenv()
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket_name = os.getenv("S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        transactions = json.load(response["Body"])
    except Exception as e:
        print(e)
        return []

    return transactions


def upload_file_s3(df: pd.DataFrame, file_name: str) -> bool:
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    buffer = StringIO()
    df.to_csv(buffer, index=False)

    # Upload the file
    load_dotenv()
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket = os.getenv("S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        s3_client.put_object(Bucket=bucket, Key=file_name, Body=buffer.getvalue())
    except Exception as e:
        print(e)
        return False
    return True


def read_file_s3(file_name):
    """Read transaction list from an S3 bucket

    :param file_name: File to read
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    load_dotenv()
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket_name = os.getenv("S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        df = pd.read_csv(response["Body"])
    except Exception as e:
        print(e)
        return pd.DataFrame(columns=COLUMNS)

    return df
