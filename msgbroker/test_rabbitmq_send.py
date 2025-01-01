import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('myuser', 'mypassword'))
#    pika.ConnectionParameters(host='172.17.0.2', credentials=pika.PlainCredentials('myuser', 'mypassword'))

)
channel = connection.channel()
channel.basic_publish(exchange='amq.topic', routing_key='topicname', body='Test message')
print("Message sent.")
connection.close()

