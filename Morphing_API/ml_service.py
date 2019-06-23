#!/usr/bin/env python3

import pika
from json import loads, dumps

from datetime import datetime

from morphing import face_to_fruits


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
    print("RECIEVED image #{} with path {}".format(r['id'], r['path']))

    resulting_path = "/tmp/{}_{}.{}".format(str(datetime.now()), r['id'], r['path'].split('.')[-1])
    face_to_fruits(r['path'], resulting_path)

    channel_send.basic_publish(
            exchange='',
            routing_key=QUEUE_RESULT,
            body=dumps({'id': r['id'], 'path': resulting_path})
    )
    print("SENT image #{} with path {}".format(r['id'], resulting_path))


_prepare()

channel_receive.basic_consume(callback=_callback, queue=QUEUE_IMAGES, no_ack=True)

channel_receive.start_consuming()
