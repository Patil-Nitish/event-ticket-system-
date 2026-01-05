# 🎟️ Event Ticket System

A comprehensive, serverless event management platform built on AWS that enables organizers to create events and attendees to register, pay, and receive digital tickets with QR codes.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Authentication & Authorization](#authentication--authorization)
- [Deployment](#deployment)
- [Cost Analysis & Scalability Plan](#cost-analysis--scalability-plan)
- [Local Development](#local-development)
- [License](#license)

## 🎯 Overview

The Event Ticket System is a fully serverless application designed to streamline event management. It provides a complete solution for event organizers to manage their events and for attendees to discover, register, and pay for events. The system automatically generates PDF tickets with QR codes that can be scanned at event venues for entry validation.

### Key Highlights

- **Serverless Architecture**: Built entirely on AWS managed services for high availability and scalability
- **Role-Based Access Control**: Separate user experiences for organizers and attendees
- **Integrated Payments**: Stripe integration for secure payment processing
- **Digital Tickets**: Auto-generated PDF tickets with QR codes stored in S3
- **Real-time Analytics**: Live event statistics including capacity, registrations, and availability
- **Mobile-Friendly**: Responsive web interface with QR code scanning capabilities

## ✨ Features

### For Event Organizers

- ✅ **Create Events**: Simple event creation with title and capacity settings
- 📊 **Real-time Dashboard**: View all created events with live statistics
- 📈 **Event Analytics**: Track registrations, capacity utilization, and event status
- 📷 **QR Ticket Scanner**: Dedicated scanning page with camera and manual input support
- ✔️ **Ticket Validation**: Mark tickets as used to prevent duplicate entries

### For Event Attendees

- 🔍 **Browse Events**: View all available events with real-time seat availability
- 💳 **Secure Payments**: Stripe-powered payment processing (₹500 per ticket)
- 🎫 **Instant Tickets**: Receive PDF tickets with QR codes immediately after registration
- ⚡ **Live Updates**: See real-time event capacity and status indicators
- 📱 **Download Tickets**: Tickets stored securely in S3 with presigned URLs

### System Features

- 🔐 **Cognito Authentication**: Secure user authentication and authorization
- 🚀 **AWS API Gateway**: HTTP API with JWT authorization
- 💾 **DynamoDB**: NoSQL database with efficient single-table design
- 📦 **S3 Storage**: Secure ticket PDF storage with automatic cleanup
- 🎨 **Modern UI**: Clean, responsive interface with gradient designs
- 🔄 **Auto-Registration**: Seamless post-payment registration flow

## 🛠️ Technology Stack

### Frontend
- **HTML5/CSS3**: Modern, responsive design with CSS variables
- **JavaScript (ES6+)**: Vanilla JS for DOM manipulation and API calls
- **html5-qrcode**: QR code scanning library for ticket validation

### Backend
- **AWS Lambda**: Serverless compute for all backend functions
  - Python 3.x for most Lambda functions
  - Node.js (ESM) for payment processing
- **AWS API Gateway**: HTTP API with JWT authorizers
- **Amazon DynamoDB**: NoSQL database with single-table design
- **Amazon S3**: Object storage for ticket PDFs
- **Amazon Cognito**: User authentication and authorization

### Third-Party Services
- **Stripe**: Payment processing platform
- **ReportLab**: Python library for PDF generation
- **qrcode**: Python library for QR code generation

### Infrastructure
- **Amazon CloudFront**: CDN for static asset delivery
- **IAM**: Role-based access control for AWS services

## 🏗️ Architecture

### High-Level Architecture

<img width="2281" height="1553" alt="architecture Event" src="https://github.com/user-attachments/assets/6d8b5f80-d415-4717-96b6-58b792572bb5" />

### Component Flow

1. **User Authentication Flow**
   - Users access the application via CloudFront
   - Cognito handles login/signup with OAuth 2.0
   - JWT tokens are returned and stored in localStorage
   - Tokens are sent with API requests for authorization

2. **Event Creation Flow** (Organizers)
   - Organizer submits event details (title, capacity)
   - API Gateway validates JWT and routes to Lambda
   - Lambda creates event record in DynamoDB
   - Response returns event ID to frontend

3. **Event Registration Flow** (Attendees)
   - Attendee selects event and initiates payment
   - Payment Lambda creates Stripe checkout session
   - User completes payment on Stripe
   - Stripe redirects back with payment confirmation
   - Registration Lambda validates capacity and creates records
   - PDF ticket with QR code is generated
   - Ticket uploaded to S3, presigned URL returned

4. **Ticket Scanning Flow** (Organizers)
   - Organizer scans QR code or enters ticket ID
   - Scan Lambda validates ticket in DynamoDB
   - Ticket status updated from VALID to USED
   - Result displayed in real-time

## 🗄️ Database Schema

### DynamoDB Table: `EventApp`

The system uses a **single-table design** with the following access patterns:

#### Primary Key Structure
- **PK (Partition Key)**: Entity identifier
- **SK (Sort Key)**: Entity type or relationship

#### Global Secondary Index (GSI1)
- **GSI1PK**: Organizer-based partitioning
- **GSI1SK**: Event-based sorting

### Entity Types

#### 1. Event Metadata
```json
{
  "PK": "EVENT#<eventId>",
  "SK": "METADATA",
  "type": "EVENT",
  "eventId": "<uuid>",
  "title": "Event Title",
  "capacity": 100,
  "organizerId": "<cognito-username>",
  "createdAt": "2024-01-01T12:00:00Z",
  "GSI1PK": "ORG#<organizerId>",
  "GSI1SK": "EVENT#<eventId>"
}
```

#### 2. Registration Record
```json
{
  "PK": "EVENT#<eventId>",
  "SK": "REG#<registrationId>",
  "type": "REGISTRATION",
  "registrationId": "<uuid>",
  "eventId": "<eventId>",
  "userId": "<cognito-username>",
  "email": "attendee@example.com",
  "ticketId": "<ticketId>",
  "createdAt": "2024-01-01T12:30:00Z"
}
```

#### 3. Ticket Record
```json
{
  "PK": "TICKET#<ticketId>",
  "SK": "METADATA",
  "type": "TICKET",
  "ticketId": "<uuid>",
  "eventId": "<eventId>",
  "userId": "<cognito-username>",
  "status": "VALID|USED",
  "issuedAt": "2024-01-01T12:30:00Z",
  "usedAt": "2024-01-01T18:00:00Z"
}
```

### Access Patterns

1. **Get Event by ID**: `Query(PK = "EVENT#<eventId>", SK = "METADATA")`
2. **Get All Registrations for Event**: `Query(PK = "EVENT#<eventId>", SK begins_with "REG#")`
3. **Get Organizer's Events**: `Query(GSI1, GSI1PK = "ORG#<userId>", GSI1SK begins_with "EVENT#")`
4. **Get All Events**: `Scan(FilterExpression: type = "EVENT" AND SK = "METADATA")`
5. **Get Ticket by ID**: `Query(PK = "TICKET#<ticketId>", SK = "METADATA")`

### Schema Diagram
<img width="6550" height="3408" alt="EventAPP" src="https://github.com/user-attachments/assets/65c9d63d-c0e5-4956-98e6-6909c122b444" />


## 📡 API Documentation

### Base URL
```
https://<api-gateway-id>.execute-api.<region>.amazonaws.com/prod
```

### Authentication
All API endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <id_token>
```

---

### 1. Create Event

**Endpoint**: `POST /events`

**Authorization**: Organizers only

**Request Body**:
```json
{
  "title": "Tech Conference 2024",
  "capacity": 500
}
```

**Response** (201 Created):
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Lambda Function**: `create_event_fn`

**Business Logic**:
- Validates user is in "organizer" group
- Generates unique event ID
- Stores event metadata in DynamoDB
- Sets up GSI for organizer-event relationship

---

### 2. List Events

**Endpoint**: `GET /events`

**Authorization**: All authenticated users

**Response** (200 OK):
```json
[
  {
    "eventId": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Tech Conference 2024",
    "capacity": 500,
    "organizerId": "john-doe"
  }
]
```

**Lambda Function**: `list_events_fn`

**Business Logic**:
- Organizers: Returns only their own events (via GSI1)
- Attendees: Returns all events (via Scan)

---

### 3. Get Event Statistics

**Endpoint**: `GET /events/{eventId}/stats`

**Authorization**: All authenticated users

**Response** (200 OK):
```json
{
  "capacity": 500,
  "registered": 347,
  "remaining": 153,
  "status": "OPEN"
}
```

**Lambda Function**: `event_stats`

**Business Logic**:
- Queries all registrations for the event
- Calculates registered count
- Computes remaining capacity
- Determines status (OPEN/FULL)

---

### 4. Register for Event

**Endpoint**: `POST /register`

**Authorization**: Attendees only

**Request Body**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "attendee@example.com"
}
```

**Response** (201 Created):
```json
{
  "registrationId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "ticketId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "ticketUrl": "https://<bucket>.s3.amazonaws.com/<path>?<presigned-params>"
}
```

**Lambda Function**: `register_fn`

**Business Logic**:
- Validates user is in "attendee" group
- Checks event exists and has capacity
- Creates registration and ticket records
- Generates QR code from ticket ID
- Creates PDF ticket with event details
- Uploads PDF to S3
- Returns presigned URL (1-hour expiry)

**Dependencies**:
- reportlab: PDF generation
- qrcode: QR code generation
- boto3: AWS SDK

---

### 5. Initiate Payment

**Endpoint**: `POST /pay`

**Authorization**: Attendees only

**Request Body**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1704384000000
}
```

**Response** (200 OK):
```json
{
  "checkoutUrl": "https://checkout.stripe.com/pay/cs_test_...",
  "sessionId": "cs_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "eventId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Lambda Function**: `pay` (Node.js)

**Business Logic**:
- Validates user is in "attendee" group
- Creates Stripe checkout session
- Sets payment amount to ₹500 (50000 INR paise)
- Configures success/cancel redirect URLs
- Returns Stripe checkout URL

**Environment Variables**:
- `STRIPE_SECRET_KEY`: Stripe API secret key
- `FRONTEND_URL`: Frontend application URL

---

### 6. Scan Ticket

**Endpoint**: `POST /scan`

**Authorization**: Organizers only

**Request Body**:
```json
{
  "ticketId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Response** (200 OK):
```json
{
  "status": "VALID"
}
```

**Possible Status Values**:
- `VALID`: Ticket is valid and has been marked as used
- `USED`: Ticket was already scanned previously
- `INVALID`: Ticket does not exist

**Lambda Function**: `scan`

**Business Logic**:
- Validates user is in "organizer" group
- Fetches ticket from DynamoDB
- Returns INVALID if ticket not found
- Returns USED if already scanned
- Updates ticket status to USED
- Adds usedAt timestamp
- Returns VALID on first scan

---

### Error Responses

All endpoints may return the following error responses:

**400 Bad Request**:
```json
{
  "error": "Missing required fields"
}
```

**403 Forbidden**:
```json
{
  "error": "Insufficient permissions"
}
```

**404 Not Found**:
```json
{
  "error": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error"
}
```

## 🔐 Authentication & Authorization

### Amazon Cognito User Pool

**User Pool ID**: `<your-user-pool-id>`

**Client ID**: `<your-client-id>`

**Domain**: `https://<your-cognito-domain>.auth.<region>.amazoncognito.com`

### User Groups

1. **organizer**
   - Can create events
   - Can view their own events
   - Can scan tickets
   - Cannot register for events

2. **attendee**
   - Can view all events
   - Can register for events
   - Can make payments
   - Cannot create events or scan tickets

### Authentication Flow

1. User clicks "Login" button
2. Redirected to Cognito Hosted UI
3. User signs up or logs in
4. Cognito returns JWT token in URL fragment
5. Frontend stores token in localStorage
6. Token included in API requests via Authorization header

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "cognito:username": "john-doe",
  "cognito:groups": ["organizer"],
  "email": "john@example.com",
  "exp": 1704470400
}
```

### Post-Signup Lambda Trigger

**Function**: `role` (lambda_function.py)

**Purpose**: Automatically adds new users to the "attendee" group

**Trigger**: Cognito Post Confirmation

## 🚀 Deployment

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.9+ (for Lambda functions)
- Node.js 18+ (for payment Lambda)
- Stripe account and API keys

### Step 1: Create DynamoDB Table

```bash
aws dynamodb create-table \
  --table-name EventApp \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes \
    IndexName=GSI1,KeySchema=[{AttributeName=GSI1PK,KeyType=HASH},{AttributeName=GSI1SK,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### Step 2: Create S3 Bucket for Tickets

```bash
aws s3 mb s3://event-tickets-<unique-suffix>
```

Configure bucket policy to allow Lambda access.

### Step 3: Create Cognito User Pool

1. Create User Pool with email sign-in
2. Create App Client (disable client secret)
3. Configure Hosted UI domain
4. Create two user groups: `organizer` and `attendee`
5. Add Post Confirmation Lambda trigger

### Step 4: Deploy Lambda Functions

For each Python Lambda:
```bash
cd lambda/<function-name>
pip install -r requirements.txt -t .
zip -r function.zip .
aws lambda create-function \
  --function-name <function-name> \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --role <lambda-execution-role-arn>
```

For Node.js payment Lambda:
```bash
cd lambda/pay
npm install
zip -r function.zip .
aws lambda create-function \
  --function-name pay \
  --runtime nodejs18.x \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --role <lambda-execution-role-arn>
```

### Step 5: Create API Gateway

1. Create HTTP API
2. Configure JWT authorizer with Cognito
3. Create routes:
   - `POST /events` → create_event_fn
   - `GET /events` → list_events_fn
   - `GET /events/{eventId}/stats` → event_stats
   - `POST /register` → register_fn
   - `POST /pay` → pay
   - `POST /scan` → scan
4. Enable CORS
5. Deploy to production stage

### Step 6: Deploy Frontend

1. Update API_BASE, COGNITO_DOMAIN, CLIENT_ID, FRONTEND in index.html
2. Upload to S3 bucket with static website hosting
3. Create CloudFront distribution
4. Update Cognito callback URLs

### Step 7: Configure Environment Variables

Set environment variables for each Lambda:
- `TABLE_NAME`: EventApp
- `TICKETS_BUCKET`: S3 bucket name
- `STRIPE_SECRET_KEY`: Stripe secret key
- `FRONTEND_URL`: CloudFront distribution URL

## 📊 Cost Analysis & Scalability Plan

For detailed information about cost breakdown and scalability strategies, please refer to the [Cost and Scalability Report PDF](Cost_Analysis_and_Scaling_Breakdown.pdf).

The report includes:
- Monthly cost estimates for AWS services
- Cost optimization strategies
- Scaling strategies for different load levels
- Multi-region deployment architecture
- Monitoring and disaster recovery plans

## 💻 Local Development

### Prerequisites

- Python 3.9+
- Node.js 18+
- AWS CLI
- AWS SAM CLI (optional, for local Lambda testing)

### Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Patil-Nitish/event-ticket-system-.git
   cd event-ticket-system-
   ```

2. **Install Python Dependencies**
   ```bash
   # For register_fn (example)
   cd lambda/register_fn
   pip install reportlab qrcode boto3 pillow
   ```

3. **Install Node.js Dependencies**
   ```bash
   cd lambda/pay
   npm install
   ```

4. **Configure Environment Variables**
   Create a `.env` file in each Lambda directory:
   ```
   TABLE_NAME=EventApp
   TICKETS_BUCKET=your-bucket-name
   STRIPE_SECRET_KEY=sk_test_...
   FRONTEND_URL=http://localhost:8000
   ```

5. **Run Frontend Locally**
   ```bash
   cd Frontend
   python -m http.server 8000
   ```
   Open http://localhost:8000 in your browser

### Testing Lambda Functions Locally

**Using AWS SAM**:

1. Create `template.yaml` (SAM template)
2. Run `sam build`
3. Run `sam local start-api`
4. Test endpoints at http://localhost:3000

**Using Python REPL**:
```python
import json
from lambda_function import lambda_handler

event = {
    "body": json.dumps({"eventId": "test-123", "email": "test@example.com"}),
    "requestContext": {
        "authorizer": {
            "jwt": {
                "claims": {
                    "cognito:username": "test-user",
                    "cognito:groups": ["attendee"]
                }
            }
        }
    }
}

result = lambda_handler(event, None)
print(result)
```

### Frontend Development

1. **Update API Configuration**
   Edit `Frontend/index.html`:
   ```javascript
   const API_BASE = "http://localhost:3000"; // SAM local API
   ```

2. **Mock Authentication**
   Store a test token in localStorage:
   ```javascript
   localStorage.setItem("id_token", "test-token");
   ```

3. **Test Payment Flow**
   Use Stripe test card: `4242 4242 4242 4242`



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


