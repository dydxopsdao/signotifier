# Code adapted from: https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html

import time

import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


# seconds; the AWS limit is 14 emails per second
DELAY_PER_EMAIL = 0.08


class Mailer:
    def __init__(self, sender, region, logger) -> None:
        self.client = boto3.client("ses", region_name=region)
        self.sender = sender
        self.logger = logger

    def send(
        self,
        subject: str,
        content: str,
        unified_message: bytes,
        signature: bytes,
        recipient: str,
        delay=DELAY_PER_EMAIL,
    ):
        try:
            # Docs:
            # - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses/client/send_raw_email.html
            # - https://docs.aws.amazon.com/ses/latest/dg/send-email-raw.html
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = recipient
            msg_body = MIMEMultipart("alternative")

            textpart = MIMEText(content.encode("utf-8"), "plain", "UTF-8")
            msg.attach(textpart)

            attachment_1 = MIMEApplication(unified_message)
            attachment_1.add_header(
                "Content-Disposition",
                "attachment",
                filename="message.txt",
            )

            attachment_2 = MIMEApplication(signature)
            attachment_2.add_header(
                "Content-Disposition",
                "attachment",
                filename="signature.sig",
            )

            msg.attach(msg_body)
            msg.attach(attachment_1)
            msg.attach(attachment_2)

            response = self.client.send_raw_email(
                Source=self.sender,
                Destinations=[recipient],
                RawMessage={
                    "Data": msg.as_string(),
                },
            )
        except ClientError as e:
            self.logger.info(e.response["Error"]["Message"])
        else:
            self.logger.info(
                f"Email sent! Message ID: {response['MessageId']}. Waiting {delay} seconds."
            )
            time.sleep(delay)
