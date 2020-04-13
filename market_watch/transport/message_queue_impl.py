import boto3
from typing import List
from .message_queue_base import MessageQueue
from ..models import ProductRef, Platform


class MessageQueueImpl(MessageQueue):
    def __init__(self, config: dict):
        session = boto3.session.Session()
        if not config['within_lambda']:
            self.sqs_client = session.client(
                'sqs',
                region_name=config['sqs']['region_name'],
                aws_access_key_id=config['sqs']['access_key'],
                aws_secret_access_key=config['sqs']['secret_key'],
            )
        else:
            self.sqs_client = session.client(
                'sqs',
                region_name=config['sqs']['region_name'],
            )
        self.sqs_queue_url = config['sqs']["queue_url"]

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
