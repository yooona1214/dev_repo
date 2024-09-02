import pika

HOST_NAME = "localhost"
QUEUE_NAME = "Chat"
QUEUE_NAME2 = "Chat2"


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)




    def callback1(ch, method, properties, body):
        message = body.decode('utf-8')  # 바이트를 문자열로 디코딩
        #print("Received message:", message)

        res = '\nAI:'+message +'라고 보내셨군요?'
        # 메시지를 다시 보내기
        send_message(res)
    
    channel.basic_consume(queue=QUEUE_NAME,
                          on_message_callback=callback1,
                          auto_ack=True)

    def callback2(ch, method, properties, body):
        message = body.decode('utf-8')  # 바이트를 문자열로 디코딩
        #print("Received message:", message)

        res = '\nAI:'+message +'라고 보내셨군요?22'
        # 메시지를 다시 보내기
        send_message(res)
        
    channel.basic_consume(queue=QUEUE_NAME,
                        on_message_callback=callback2,
                        auto_ack=True)    
    
   

    try:
        print("Waiting for messages.")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print('Ctrl+C is Pressed.')


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME2)

    channel.basic_publish(exchange='', routing_key=QUEUE_NAME2, body=message)
    #print(f"Sent message.\n{message}")

    connection.close()


if __name__ == '__main__':
    main()