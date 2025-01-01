import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('myuser', 'mypassword'))
)
channel = connection.channel()

def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")

channel.basic_consume(queue='test_queue', on_message_callback=callback, auto_ack=True)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()

