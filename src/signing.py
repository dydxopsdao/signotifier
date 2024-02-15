import base64

import boto3
from botocore.exceptions import ClientError


SIGNING_ALGORITHM = "RSASSA_PSS_SHA_256"


class Signer:
    def __init__(self, region, key_id, logger, algorithm=SIGNING_ALGORITHM) -> None:
        self.client = boto3.client("kms", region_name=region)
        self.key_id = key_id
        self.algorithm = algorithm
        self.logger = logger

    def sign(self, message: bytes) -> bytes:
        self.logger.info(f"Signing: key_id={self.key_id} algorithm={self.algorithm} message_length={len(message)}")
        self.logger.info(f"Message:")
        self.logger.info(message)
        try:
            # Docs:
            # - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms/client/sign.html
            response = self.client.sign(
                KeyId=self.key_id,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm=self.algorithm,
            )
            signature = response["Signature"]
        except ClientError as e:
            self.logger.info(e.response["Error"]["Message"])

        self.logger.info("Signature created:")
        self.logger.info(signature)

        return signature
