import pika
import json


with open('/workspace/ssl_project/output/metadata.json') as f:
    data = json.load(f)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('myuser', 'mypassword'))
)


channel = connection.channel()
#channel.basic_publish(exchange='amq.topic', routing_key='topicname', body='metadata')

# Replace 'test_queue' with your actual queue name
#channel.queue_declare(queue='test_queue')

channel.basic_publish(exchange='amq.topic',
                      routing_key='topicname',
                      body=json.dumps(data))

print("Message sent.")

connection.close()
