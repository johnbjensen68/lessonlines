"""
Lambda handler for LessonLines API.
Uses Mangum to adapt FastAPI for AWS Lambda.
"""
import json
import os
import boto3
from mangum import Mangum

# Get database credentials from Secrets Manager if running in Lambda
if os.environ.get('DATABASE_SECRET_ARN'):
    secrets_client = boto3.client('secretsmanager')
    try:
        secret_response = secrets_client.get_secret_value(
            SecretId=os.environ['DATABASE_SECRET_ARN']
        )
        secret = json.loads(secret_response['SecretString'])

        # Set environment variables for database connection
        os.environ['DATABASE_USER'] = secret['username']
        os.environ['DATABASE_PASSWORD'] = secret['password']

        # Construct DATABASE_URL for SQLAlchemy
        db_host = os.environ.get('DATABASE_HOST', 'localhost')
        db_port = os.environ.get('DATABASE_PORT', '5432')
        db_name = os.environ.get('DATABASE_NAME', 'lessonlines')
        os.environ['DATABASE_URL'] = (
            f"postgresql://{secret['username']}:{secret['password']}"
            f"@{db_host}:{db_port}/{db_name}"
        )
    except Exception as e:
        print(f"Error retrieving database secret: {e}")
        raise

from app.main import app

# Create Mangum handler
handler = Mangum(app, lifespan="off")
