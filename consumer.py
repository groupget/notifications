import pika

import config


def start_consuming():
    print("start_consuming")
    url = config.rabbit_address
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange='groupget_events',
                             exchange_type='topic')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='groupget_events',
                       queue=queue_name,
                       routing_key='item.created')
    channel.basic_consume(callback_orders,
                          queue=queue_name,
                          no_ack=True)
    channel.start_consuming()


def callback_orders(ch, method, properties, body):
    print("Received notification: {}".format(body))
    # body_dict = ast.literal_eval(body.decode('utf-8'))
    # print("Received notification: {}".format(body_dict))
    # send_web_push(body_dict)
