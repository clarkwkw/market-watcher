import boto3
from typing import List
from .message_queue_base import MessageQueue
from ..models import ProductRef, Platform


class MessageQueueImpl(MessageQueue):
    def __init__(self, sqs_config: dict):
        session = boto3.session.Session()
        self.sqs_client = session.client(
            'sqs',
            region_name=sqs_config['region_name'],
            aws_access_key_id=sqs_config['access_key'],
            aws_secret_access_key=sqs_config['secret_key'],
        )
        self.sqs_queue_url = sqs_config["queue_url"]

    def notify_updates(self, product_refs: List[ProductRef]):
        for pr in product_refs:
            self.sqs_client.send_message(
                QueueUrl=self.sqs_queue_url,
                MessageAttributes={
                    "platform": {
                        'DataType': "String",
                        'StringValue': pr.platform.value
                    },
                    "id": {
                        'DataType': "String",
                        'StringValue': pr.id
                    }
                },
                MessageBody=f"Product updated: {pr.platform.value}-{pr.id}"
            )

    @classmethod
    def parse_sqs_notification(self, notification: dict) -> List[ProductRef]:
        product_refs = []
        for record_dict in notification.get("records", []):
            product_refs.append(ProductRef(
                Platform(record_dict["messageAttributes"]["platform"]),
                record_dict["messageAttributes"]["id"]
            ))
        return product_refs
