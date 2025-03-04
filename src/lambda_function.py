import base64
import json
import logging
import os

from mailing import Mailer
from signing import Signer
from typing import Tuple

logger = logging.getLogger()
logger.setLevel(logging.INFO)


MAX_MESSAGE_LENGTH = 4096


class MessageTooLongError(Exception):
    pass


def run(event, context):
    caller_arn = event["requestContext"]["authorizer"]["iam"]["userArn"]
    logger.info(f"Caller ARN: {caller_arn}")

    try:
        subject, unified_message, decorated_content = validate_input(event)
    except MessageTooLongError as e:
        logger.info("Message is too long")
        return {
            "statusCode": 400,
            "body": f"Message is too long. Maximum length is {MAX_MESSAGE_LENGTH}.",
        }
    except Exception as e:
        logger.info(f"Input validation failed: {e}")
        return {"statusCode": 400}

    kms_signer = Signer(
        region=os.environ["EMAIL_AWS_REGION"],
        key_id=os.environ["KMS_SIGNING_KEY_ID"],
        logger=logger,
    )
    kms_signature = kms_signer.sign(unified_message)

    send_emails(subject, decorated_content, unified_message, kms_signature)

    response = {
        "signature_base64": base64.b64encode(kms_signature).decode("ascii"),
    }
    return json.dumps(response)


def validate_input(event) -> Tuple[str, bytes, str]:
    body_string = (
        base64.b64decode(event["body"]) if event["isBase64Encoded"] else event["body"]
    )
    body = json.loads(body_string)

    subject = body["subject"]
    content = body["content"].encode('utf-8').decode('unicode_escape')
    logger.info(f"Subject: {subject}; Content: {content}")

    unified_message = f"{subject}\n\n{content}".encode("utf-8")
    if len(unified_message) > MAX_MESSAGE_LENGTH:
        raise MessageTooLongError()

    decorated_content = decorate_content(content)

    return subject, unified_message, decorated_content


def decorate_content(original_message: str) -> str:
    decorated_message = (
        f"{original_message}\n\n"
        "-----\n"
        "To verify the authenticity of this message:\n\n"
        "1) Download the two attached files - one with the message and one with the RSA signature.\n"
        "2) Download the dYdX Ops Services public key from https://github.com/dydxopsdao/signotifier/blob/main/dydxops-pubkey.pem as `dydxops-pubkey.pem`.\n"
        "3) Run:\n"
        "openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.sig -sigopt rsa_padding_mode:pss message.txt\n\n"
        "You should see: 'Verified OK'.\n"
    )
    return decorated_message


def send_emails(
    subject: str, decorated_content: str, unified_message: bytes, signature: bytes
):
    email_client = Mailer(
        sender=os.environ["SENDER"],
        region=os.environ["EMAIL_AWS_REGION"],
        logger=logger,
    )
    for recipient_raw in os.environ["RECIPIENTS"].split(","):
        recipient_cleaned = recipient_raw.strip()
        if not recipient_cleaned:
            continue
        logger.info(f"Sending to: {recipient_cleaned}")
        email_client.send(
            subject=subject,
            content=decorated_content,
            unified_message=unified_message,
            signature=signature,
            recipient=recipient_cleaned,
        )
