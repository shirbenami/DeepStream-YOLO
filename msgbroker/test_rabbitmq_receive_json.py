import pika
import json 
import os


OUTPUT_DIR = '/workspace/ssl_project/output'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'received_messages.txt')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def callback(ch, method, properties, body):
    message = body.decode('utf-8')
    #print(f" [x] Received message: {message}")

    with open(OUTPUT_FILE, "a") as file:
        file.write(message + "\n")

    ch.basic_ack(delivery_tag=method.delivery_tag)

    return message


def main():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('myuser', 'mypassword')))
    channel = connection.channel()


    channel.basic_consume(queue='test_queue',
                          on_message_callback=callback,
                          auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
