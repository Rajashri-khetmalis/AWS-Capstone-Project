import os
import boto3
from moto import mock_aws

# -------------------------------------------------
# MOCK AWS CREDENTIALS (Required by boto3)
# -------------------------------------------------
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# -------------------------------------------------
# START MOTO MOCK (Intercepts all AWS calls)
# -------------------------------------------------
mock = mock_aws()
mock.start()

# Import app AFTER mock starts
from app_aws import app
import app_aws


def setup_infrastructure():
    print(">>> Creating Mock AWS Infrastructure...")

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')

    # ------------------ DynamoDB Tables ------------------

    # Users Table
    dynamodb.create_table(
        TableName='Users',
        KeySchema=[{'AttributeName': 'username', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'username', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    # Admin Users Table
    dynamodb.create_table(
        TableName='AdminUsers',
        KeySchema=[{'AttributeName': 'username', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'username', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    # Projects Table
    dynamodb.create_table(
        TableName='Projects',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    # Enrollments Table
    dynamodb.create_table(
        TableName='Enrollments',
        KeySchema=[{'AttributeName': 'username', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'username', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    # ------------------ SNS Topic ------------------
    response = sns.create_topic(Name='aws_capstone_topic')
    app_aws.SNS_TOPIC_ARN = response['TopicArn']

    print(">>> Mock AWS Setup Completed")
    print(f">>> SNS Topic ARN: {app_aws.SNS_TOPIC_ARN}")


if __name__ == '__main__':
    try:
        setup_infrastructure()
        print("\n>>> Running Blood Bridge (AWS Mock Mode)")
        print(">>> URL: http://localhost:5000")
        print(">>> Press CTRL + C to stop")

        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # IMPORTANT: Prevents losing mock state
        )

    finally:
        mock.stop()
