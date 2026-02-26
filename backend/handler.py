"""
Lambda handler for LessonLines API.
Uses Mangum to adapt FastAPI for AWS Lambda.

Supports multiple modes:
- API requests: routed to FastAPI via Mangum (default)
- Migrations: triggered with {"action": "migrate"} payload
- Seed: triggered with {"action": "seed"} payload
- Make admin: triggered with {"action": "make_admin", "email": "...", "password": "..."} payload
"""
import json
import os
import io
import logging
from pathlib import Path

import boto3
from mangum import Mangum

logger = logging.getLogger(__name__)

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

# Create Mangum handler for API requests
_api_handler = Mangum(app, lifespan="off")


def _run_migration(command="upgrade", revision="head"):
    """Run Alembic migration commands programmatically."""
    from alembic.config import Config
    from alembic import command as alembic_command

    # Configure Alembic
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(Path(__file__).parent / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

    # Capture Alembic output
    output_buffer = io.StringIO()
    alembic_cfg.print_stdout = lambda msg, *args: output_buffer.write(msg % args + "\n")

    if command == "current":
        alembic_command.current(alembic_cfg, verbose=True)
    elif command == "upgrade":
        alembic_command.upgrade(alembic_cfg, revision)
    elif command == "downgrade":
        alembic_command.downgrade(alembic_cfg, revision)
    elif command == "history":
        alembic_command.history(alembic_cfg, verbose=True)
    else:
        raise ValueError(f"Unsupported migration command: {command}")

    return output_buffer.getvalue()


def handler(event, context):
    """Main Lambda handler. Routes to migration or API based on event payload."""
    if isinstance(event, dict) and event.get("action") == "migrate":
        command = event.get("command", "upgrade")
        revision = event.get("revision", "head")

        logger.info(f"Running migration: {command} {revision}")

        try:
            output = _run_migration(command=command, revision=revision)
            return {
                "statusCode": 200,
                "body": {
                    "success": True,
                    "command": command,
                    "revision": revision,
                    "output": output,
                },
            }
        except Exception as e:
            logger.exception("Migration failed")
            return {
                "statusCode": 500,
                "body": {
                    "success": False,
                    "command": command,
                    "revision": revision,
                    "error": str(e),
                },
            }

    if isinstance(event, dict) and event.get("action") == "seed":
        logger.info("Running database seed")
        try:
            from app.seed import run_seed
            run_seed()
            return {
                "statusCode": 200,
                "body": {"success": True, "action": "seed"},
            }
        except Exception as e:
            logger.exception("Seed failed")
            return {
                "statusCode": 500,
                "body": {"success": False, "action": "seed", "error": str(e)},
            }

    if isinstance(event, dict) and event.get("action") == "deduplicate_events":
        logger.info("Deduplicating events: removing source_id=NULL events that have a source_id counterpart")
        try:
            from app.database import SessionLocal
            from app.models import Event, TimelineEvent
            from sqlalchemy import text

            db = SessionLocal()
            try:
                # Find all events without source_id that share a title+topic with a source_id event
                old_events = db.query(Event).filter(Event.source_id == None).all()
                deleted = 0
                reassigned = 0

                for old in old_events:
                    # Find the canonical replacement (same title + topic, has source_id)
                    new = db.query(Event).filter(
                        Event.source_id != None,
                        Event.title == old.title,
                        Event.topic_id == old.topic_id,
                    ).first()

                    if new:
                        # Reassign any timeline_events pointing to the old event
                        count = db.query(TimelineEvent).filter(TimelineEvent.event_id == old.id).update(
                            {"event_id": new.id}
                        )
                        reassigned += count
                        db.delete(old)
                        deleted += 1

                db.commit()
                return {
                    "statusCode": 200,
                    "body": {"success": True, "deleted": deleted, "timeline_events_reassigned": reassigned},
                }
            finally:
                db.close()
        except Exception as e:
            logger.exception("Deduplication failed")
            return {"statusCode": 500, "body": {"success": False, "error": str(e)}}

    if isinstance(event, dict) and event.get("action") == "import_events":
        logger.info("Running event import from JSON files")
        try:
            from pathlib import Path
            from app.database import SessionLocal
            from app.services.import_events import import_all_event_files

            data_dir = Path(__file__).parent / "event-data"
            db = SessionLocal()
            try:
                results = import_all_event_files(db, data_dir)
                db.commit()
                return {
                    "statusCode": 200,
                    "body": {"success": True, "results": results},
                }
            finally:
                db.close()
        except Exception as e:
            logger.exception("Event import failed")
            return {
                "statusCode": 500,
                "body": {"success": False, "error": str(e)},
            }

    if isinstance(event, dict) and event.get("action") == "make_admin":
        email = event.get("email")
        password = event.get("password")
        if not email:
            return {"statusCode": 400, "body": {"success": False, "error": "email is required"}}

        logger.info(f"Making admin user: {email}")
        try:
            from app.database import SessionLocal
            from app.models import User
            from app.services.auth import get_password_hash

            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    user.is_admin = True
                    action = "promoted"
                elif password:
                    user = User(
                        email=email,
                        hashed_password=get_password_hash(password),
                        display_name="Admin",
                        is_admin=True,
                    )
                    db.add(user)
                    action = "created"
                else:
                    return {"statusCode": 400, "body": {"success": False, "error": "User not found; provide password to create"}}
                db.commit()
                return {"statusCode": 200, "body": {"success": True, "email": email, "action": action}}
            finally:
                db.close()
        except Exception as e:
            logger.exception("Make admin failed")
            return {"statusCode": 500, "body": {"success": False, "error": str(e)}}

    # Default: route to FastAPI via Mangum
    return _api_handler(event, context)
