import json
import os
import uuid
import boto3
from datetime import datetime
from decimal import Decimal

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        title = body.get("title")
        capacity = body.get("capacity")

        if not title or capacity is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "title and capacity required"})
            }

        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        username = claims["cognito:username"]
        groups = claims.get("cognito:groups", [])

        if "organizer" not in groups:
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "Only organizers can create events"})
            }

        event_id = str(uuid.uuid4())

        item = {
            "PK": f"EVENT#{event_id}",
            "SK": "METADATA",
            "type": "EVENT",

            "eventId": event_id,
            "title": title,
            "capacity": Decimal(str(capacity)),
            "organizerId": username,
            "createdAt": datetime.utcnow().isoformat(),

            "GSI1PK": f"ORG#{username}",
            "GSI1SK": f"EVENT#{event_id}"
        }

        table.put_item(Item=item)

        return {
            "statusCode": 201,
            "body": json.dumps({"eventId": event_id})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
