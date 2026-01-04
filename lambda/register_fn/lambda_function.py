import json
import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from io import BytesIO
from reportlab.lib.utils import ImageReader
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------
# Environment
# -------------------------
TABLE_NAME = os.environ["TABLE_NAME"]
TICKETS_BUCKET = os.environ["TICKETS_BUCKET"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")

# -------------------------
# Helpers
# -------------------------
def generate_qr(ticket_id: str) -> BytesIO:
    img = qrcode.make(ticket_id)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def generate_pdf(event_title, email, ticket_id, qr_buffer) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, height - 50, "🎟 Event Ticket")

    # Body
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 100, f"Event: {event_title}")
    c.drawString(40, height - 120, f"Email: {email}")
    c.drawString(40, height - 140, f"Ticket ID: {ticket_id}")

    # QR
    qr_image = ImageReader(qr_buffer)
    c.drawImage(
        qr_image,
        40,
        height - 340,
        width=160,
        height=160
    )

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(40, 50, "Present this QR code at the event entry")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# -------------------------
# Lambda Handler
# -------------------------
def lambda_handler(event, context):
    try:
        # -------------------------
        # Parse body
        # -------------------------
        body = json.loads(event.get("body", "{}"))
        event_id = body.get("eventId")
        email = body.get("email")

        if not event_id or not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "eventId and email required"})
            }

        # -------------------------
        # Auth
        # -------------------------
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        username = claims.get("cognito:username") or claims.get("username")
        groups = claims.get("cognito:groups", [])

        if "attendee" not in groups:
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "Only attendees can register"})
            }

        # -------------------------
        # Fetch event
        # -------------------------
        event_resp = table.get_item(
            Key={
                "PK": f"EVENT#{event_id}",
                "SK": "METADATA"
            }
        )

        if "Item" not in event_resp:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Event not found"})
            }

        event_item = event_resp["Item"]
        capacity = int(event_item["capacity"])
        event_title = event_item["title"]

        # -------------------------
        # Capacity check
        # -------------------------
        reg_resp = table.query(
            KeyConditionExpression=
                Key("PK").eq(f"EVENT#{event_id}") &
                Key("SK").begins_with("REG#")
        )

        if reg_resp["Count"] >= capacity:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Event is full"})
            }

        # -------------------------
        # Create records
        # -------------------------
        registration_id = str(uuid.uuid4())
        ticket_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        registration_item = {
            "PK": f"EVENT#{event_id}",
            "SK": f"REG#{registration_id}",
            "type": "REGISTRATION",
            "registrationId": registration_id,
            "eventId": event_id,
            "userId": username,
            "email": email,
            "ticketId": ticket_id,
            "createdAt": now
        }

        ticket_item = {
            "PK": f"TICKET#{ticket_id}",
            "SK": "METADATA",
            "type": "TICKET",
            "ticketId": ticket_id,
            "eventId": event_id,
            "userId": username,
            "status": "VALID",
            "issuedAt": now
        }

        with table.batch_writer() as batch:
            batch.put_item(Item=registration_item)
            batch.put_item(Item=ticket_item)

        # -------------------------
        # QR + PDF
        # -------------------------
        qr_buffer = generate_qr(ticket_id)
        pdf_buffer = generate_pdf(event_title, email, ticket_id, qr_buffer)

        s3_key = f"{event_id}/{ticket_id}.pdf"

        s3.put_object(
            Bucket=TICKETS_BUCKET,
            Key=s3_key,
            Body=pdf_buffer,
            ContentType="application/pdf"
        )

        ticket_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": TICKETS_BUCKET,
                "Key": s3_key
            },
            ExpiresIn=3600
        )

        # -------------------------
        # Response (extended only)
        # -------------------------
        return {
            "statusCode": 201,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "registrationId": registration_id,
                "ticketId": ticket_id,
                "ticketUrl": ticket_url
            })
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
