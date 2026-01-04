import json
import os
import boto3
from datetime import datetime

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        ticket_id = body.get("ticketId")

        if not ticket_id:
            return response(400, {"error": "ticketId required"})

        # Auth
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        groups = claims.get("cognito:groups", [])

        if "organizer" not in groups:
            return response(403, {"error": "Not authorized to scan tickets"})

        # Fetch ticket
        res = table.get_item(
            Key={
                "PK": f"TICKET#{ticket_id}",
                "SK": "METADATA"
            }
        )

        if "Item" not in res:
            return response(200, {"status": "INVALID"})

        ticket = res["Item"]

        if ticket["status"] == "USED":
            return response(200, {"status": "USED"})

        # Mark as used
        table.update_item(
            Key={
                "PK": f"TICKET#{ticket_id}",
                "SK": "METADATA"
            },
            UpdateExpression="SET #s = :s, usedAt = :u",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "USED",
                ":u": datetime.utcnow().isoformat()
            }
        )

        return response(200, {"status": "VALID"})

    except Exception as e:
        return response(500, {"error": "Internal error"})


def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
