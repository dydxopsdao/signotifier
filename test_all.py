import base64
import json
import os
from unittest import mock
from unittest.mock import patch

from src import lambda_function


def test_success():
    os.environ["EMAIL_AWS_REGION"] = "region"
    os.environ["SENDER"] = "sender"
    os.environ["KMS_SIGNING_KEY_ID"] = "key-id"

    with mock.patch("boto3.client", MockedBoto3ClientFactory) as mocked_boto3_client:
        result_raw = lambda_function.run(
            {
                "headers": {"authorization": "Bearer secret"},
                "body": base64.b64encode(
                    json.dumps(
                        {
                            "subject": "test-subject",
                            "content": "test-content",
                            "recipients": "test1@test.com,test2@test.com"
                        }
                    ).encode("ascii")
                ).decode("ascii"),
                "isBase64Encoded": True,
                "requestContext": {
                    "authorizer": {
                        "iam": {
                            "userArn": "arn:aws:iam::123456789012:user/test-user",
                        }
                    }
                },
            },
            None,
        )

    # "dGVzdC1zaWduYXR1cmU=" is base64-encoded "test-signature"
    assert result_raw == '{"signature_base64": "dGVzdC1zaWduYXR1cmU="}'
    assert len(mocked_boto3_client.instances) == 2
    mocked_boto3_client.instances[0].sign.assert_called_once_with(
        KeyId="key-id",
        Message=b"test-subject\n\ntest-content",
        MessageType="RAW",
        SigningAlgorithm="RSASSA_PSS_SHA_256",
    )
    assert mocked_boto3_client.instances[1].send_raw_email.call_count == 2


class MockedBoto3ClientFactory:
    instances = []

    def __new__(cls, *args, **kwargs):
        client = mock.Mock()
        client.sign = mock.Mock(return_value={"Signature": b"test-signature"})
        client.send_raw_email = mock.Mock(return_value={"MessageId": "test-message-id"})
        cls.instances.append(client)
        return client
