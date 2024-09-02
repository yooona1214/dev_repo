"""Chat proccesor"""

import pika


HOST_NAME = "localhost"
QUEUE_NAME = "Chat"

RESPONSE = None


class ChatProdCons(object):
    """Chatprocessor module"""

    def __init__(self):
        self.connection_cons = pika.BlockingConnection(
            pika.ConnectionParameters(host=HOST_NAME)
        )
        self.connection_prod = pika.BlockingConnection(
            pika.ConnectionParameters(host=HOST_NAME)
        )
        self.channel_cons = self.connection_cons.channel()
        self.channel_prod = self.connection_prod.channel()
        self.response = None

    def initialize_response(self):
        """init response"""
        self.response = None

    def sender(self, msg, user_id):
        """sender"""
        QUEUE_NAME2 = user_id
        self.channel_prod.queue_declare(queue=QUEUE_NAME)
        self.channel_cons.queue_declare(queue=QUEUE_NAME2)

        print("chat_processor SENDER: ", msg)
        self.channel_prod.basic_publish(exchange="", routing_key=QUEUE_NAME, body=msg)
        self.connection_prod.close()
        self.receiver(QUEUE_NAME2)

    def receiver(self, queue_name):
        """receiver"""
        self.channel_cons.basic_consume(
            queue=queue_name, on_message_callback=self.cons_callback, auto_ack=True
        )

        try:
            print("Waiting for response.")
            self.channel_cons.start_consuming()

        except KeyboardInterrupt:
            print("Ctrl C")

    def cons_callback(self, ch, method, properties, body):
        """cons_callback"""
        message = body.decode("utf-8")  # 바이트를 문자열로 디코딩
        self.response = message
        print("cons_callback: ", self.response)
        self.connection_cons.close()

    def return_response(self):
        """return_response"""
        while True:
            if self.response is not None:
                return str(self.response)
            else:
                pass
