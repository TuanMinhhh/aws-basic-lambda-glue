import boto3
import json

lambda_client = boto3.client("lambda","ap-southeast-1")

event = {
    "schema_name": "ai4e_test",
    "table_name": "card_type",
    "bucket_name": "ai4e-ap-southeast-1-dev-s3-data-landing",
    "object_key": "raw_zone/minhpt1_test/minhpt1_test.json"
}

response = lambda_client.invoke(
    FunctionName = 'lbd-func-minhpt1_crawler',
    Payload = json.dumps(event, default=str)
)