from typing import List
import boto3
from .message_queue_base import MessageQueue
from ..models import ProductRef, Platform


class MessageQueueImpl(MessageQueue):
    def __init__(self, config: dict, queue_name: str):
        session = boto3.session.Session()
        if not config['within_lambda']:
            self.sqs_client = session.client(
                'sqs',
                region_name=config['sqs']['region_name'],
                aws_access_key_id=config['sqs']['access_key'],
                aws_secret_access_key=config['sqs']['secret_key'],
            )
        else:
            self.sqs_client = session.client('sqs')
        self.sqs_queue_url = self.sqs_client.get_queue_url(
            QueueName=queue_name
        )["QueueUrl"]

    def enqueue(self, product_refs: List[ProductRef]):
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
                MessageBody=f"Notify product: {pr.platform.value}-{pr.id}"
            )

    @classmethod
    def deserialize(self, d: dict) -> List[ProductRef]:
        product_refs = []
        for record_dict in d.get("Records", []):
            product_refs.append(ProductRef(
                Platform(record_dict["messageAttributes"]
                         ["platform"]["stringValue"]),
                record_dict["messageAttributes"]["id"]["stringValue"]
            ))
        return product_refs
