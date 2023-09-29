import boto3
from enum import enum
from dotenv import load_dotenv
import requests
import json
import os
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from circles_local_database_python.connector import connector
from circles_local_database_python.generic_crud import GenericCRUD
from http import HTTPStatus

load_dotenv()

# Initialize the logger
SMS_AWS_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 208
SMS_AWS_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "sms_message_aws_local_python_package"
DEVELOPER_EMAIL = "Enter your circlez.ai email"
 
logger = Logger.create_logger(object={
    'component_id': SMS_AWS_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': SMS_AWS_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
})
# Function to send an SMS
def send_sms(phone_number, message):
    try:
        logger.start("sms message send", object={"phone": phone_number, "message": message,})

        # Create an SNS client
        client = boto3.client(
            "sns",
            aws_access_key_id="AKIAQRH3QJFEC5EYUP7V",
            aws_secret_access_key="U1+aH0cqoiLHN9PXk/eoy/JZWxFMY1Ed+WTuAMj4",  
            region_name="il-central-1"
        )

        # Send your SMS message
        response = client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        
        # Log success
        if response.status_code == HTTPStatus.OK:
            logger.info({"message": "SMS sent successfully.", "message_id": response['MessageId']})
            logger.info("MessageId: " + response.text)
        else:
            logger.error({"message": f"SMS sending failed to {phone_number} with status code: {response.status_code}"})
    except Exception as e:
        # Log error and exception
        logger.exception("Sending to WhatsApp failed", object=e)
        logger.end()
        raise
    finally:
        logger.end("aws sms message send")
   