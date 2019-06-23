"""
This is a dummy pika receiver.
The ML-pika interaction must work in a similar way
"""

import pika
from json import loads


QUEUE_IMAGES = 'images'
QUEUE_RESULT = 'result'


connection = None
channel_send = None
channel_receive = None


def _prepare():
    """
    Prepare pika connection
    """
    global connection
    global channel_send
    global channel_receive

    if connection is not None:
        return

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel_receive = connection.channel()
    channel_receive.queue_declare(queue=QUEUE_IMAGES)

    channel_send = connection.channel()
    channel_send.queue_declare(queue=QUEUE_RESULT)


def _callback(channel, method, properties, body):
    r = loads(body)
    print("Received image {} at path {}".format(r['id'], r['path']))
    channel_send.basic_publish(
            exchange='',
            routing_key=QUEUE_RESULT,
            body=body
    )


_prepare()

channel_receive.basic_consume(_callback, queue=QUEUE_IMAGES, no_ack=True)

channel_receive.start_consuming()
