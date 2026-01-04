import boto3

cognito = boto3.client("cognito-idp")

def lambda_handler(event, context):
    cognito.admin_add_user_to_group(
        UserPoolId=event["userPoolId"],
        Username=event["userName"],
        GroupName="attendee"
    )
    return event
