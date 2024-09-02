from datetime import datetime
import pika

HOST_NAME = "localhost"
QUEUE_NAME = "Chat"
QUEUE_NAME2 = "Chat2"


def chat_processor(msg):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)
    
    # 메시지 송신
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=msg)

    # 응답 수신
    response=receive_response()

    connection.close()
    
    return response


def receive_response():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME2)

    def callback(ch, method, properties, body):
        message = body.decode('utf-8')  # 바이트를 문자열로 디코딩
        return message

    channel.basic_consume(queue=QUEUE_NAME2,
                          on_message_callback=callback,
                          auto_ack=True)

    try:
        print("Waiting for response.")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print('Ctrl+C is Pressed.')



