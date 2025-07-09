from confluent_kafka import Producer
import json
from datetime import datetime

# Callback to handle message delivery
def delivery_callback(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Timestamp with milliseconds
        print(f"[{timestamp}] Message delivered to {msg.topic()} [{msg.partition()}]")

# Producer configuration
conf = {
    'bootstrap.servers': '192.168.5.247:9092',  # Kafka server
    'client.id': 'PTL-Controller-Producer1'
}

# Create Producer instance
producer = Producer(conf)

# Define the JSON message
message_data = {
    "ptlcolor": "SG",
    "controllervalue": "1008",
    "action": "Single",
    "display": "0CLSB",
    "interval": 0,
    "uid": "5",
    "deviceid": "1",
    "machine_id": "c0173915-bd47-402a-8101-ffc3bff00754",
    "user_id": "USER780",
    "actiontype": "SORT"
}

# Produce a message to a Kafka topic
def produce_message():
    # Serialize the message_data dictionary to a JSON string
    message_json = json.dumps(message_data)
    
    # Get current timestamp with milliseconds
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] Producing message: {message_json}")
    
    # Send the JSON string as the value of the Kafka message
    producer.produce('PTL-Controller-Topic', key='key', value=message_json, headers={'machine_id': message_data['machine_id']}, callback=delivery_callback)
    producer.flush()  # Wait for all messages to be delivered

if __name__ == "__main__":
    produce_message()

