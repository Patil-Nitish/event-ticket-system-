import json
import boto3

table = boto3.resource("dynamodb").Table("EventApp")

def lambda_handler(event, context):
    event_id = event["pathParameters"]["eventId"]

    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={
            ":pk": f"EVENT#{event_id}"
        }
    )

    items = resp.get("Items", [])

    metadata = None
    registered = 0

    for item in items:
        if item["SK"] == "METADATA":
            metadata = item
        elif item["SK"].startswith("REG#"):
            registered += 1

    if not metadata:
        return {
            "statusCode": 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Event not found"})
        }

    capacity = int(metadata["capacity"])
    remaining = capacity - registered

    status = "OPEN" if remaining > 0 else "FULL"

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "capacity": capacity,
            "registered": registered,
            "remaining": remaining,
            "status": status
        })
    }
