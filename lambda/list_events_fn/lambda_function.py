import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

TABLE_NAME = os.environ["TABLE_NAME"]
table = boto3.resource("dynamodb").Table(TABLE_NAME)

# ---------- helpers (MUST be above handler) ----------

def json_safe(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def extract_event_id(item):
    if "eventId" in item:
        return item["eventId"]
    return item["PK"].replace("EVENT#", "")

# ---------- lambda handler ----------

def lambda_handler(event, context):
    try:
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        username = claims["cognito:username"]
        groups = claims.get("cognito:groups", [])

        # Organizer → own events
        if "organizer" in groups:
            resp = table.query(
                IndexName="GSI1",
                KeyConditionExpression=
                    Key("GSI1PK").eq(f"ORG#{username}") &
                    Key("GSI1SK").begins_with("EVENT#")
            )
            items = resp.get("Items", [])

        # Attendee → all events
        else:
            resp = table.scan(
                FilterExpression=
                    Attr("type").eq("EVENT") &
                    Attr("SK").eq("METADATA")
            )
            items = resp.get("Items", [])

        events = []
        for e in items:
            events.append({
                "eventId": extract_event_id(e),
                "title": e.get("title", ""),
                "capacity": e.get("capacity", 0),
                "organizerId": e.get("organizerId", "")
            })

        return {
            "statusCode": 200,
            "body": json.dumps(events, default=json_safe)
        }

    except Exception as e:
        print("ERROR:", str(e))
        raise e
