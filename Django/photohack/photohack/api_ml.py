import pika
from json import dumps, loads


QUEUE_IMAGES = 'images'
QUEUE_RESULT = 'result'


connection = None
channel_send = None
channel_receive = None

db = dict()


def _prepare():
    """
    Prepare pika connection
    """
    global connection
    global channel_send
    global channel_receive

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel_send = connection.channel()
    channel_send.queue_declare(queue=QUEUE_IMAGES)

    channel_receive = connection.channel()
    channel_receive.queue_declare(queue=QUEUE_RESULT)


def send_to_ml(id: int, path: str):
    """
    Send request to ML for file processing
    """
    global channel_send

    _prepare()
    channel_send.basic_publish(
            exchange='',
            routing_key=QUEUE_IMAGES,
            body=dumps({'id': id, 'path': path})
    )


def receive_from_ml(id: int) -> str or None:
    """
    Check if file is already processed by ML
    :returns: None if no result is available
    """
    global db
    global channel_receive

    if id in db:
        return db[id]

    _prepare()

    while True:
        print("receive_from_ml check")
        ok, prop, body = channel_receive.basic_get(queue=QUEUE_RESULT, auto_ack=True)
        if ok is None:
            break

        r = loads(body)
        db[int(r['id'])] = r['path']
        print("receive_from_ml {} at {}".format(r['id'], r['path']))

    print(db)
    print("ID is {}".format(id))
    return db.get(int(id))
