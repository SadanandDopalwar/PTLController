import sys
import os


# Add the Clientdata folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
from confluent_kafka import Consumer, KafkaException, KafkaError
import datetime
import logger_file
import db_connector
import GetColor
import ptlsorting
import sockets
import ProcessPTL
import combinedata
from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio
import json
from datetime import datetime
from threading import Thread



timezone = "Asia/Kolkata"

file_path = 'settings.json'

# Write the settings to the specified JSON file
with open(file_path, 'r') as f:
    settings = json.load(f)

machineid = settings.get("machineid")
namedb = settings['database']['dbname']
userdb = settings['database']['user']
passworddb = settings['database']['password']
hostdb = settings['database']['host']
portdb = settings['database']['port']
controllerport = settings.get("controllerport")
log_file_path = settings.get("log_file_path")
PTL_IP = settings.get("PTL_IP")
PTL_PORT = settings.get("PTL_PORT")
IsMultiUser = settings.get("IsMultiUser")
MultiColors = settings.get("MultiColors")
color1 = MultiColors.split(",")[0]
color2 = MultiColors.split(",")[1]
# Extracting the logger file
logger = logger_file.logging_handler(log_file_path)

# Connecting to the Database
logger.info("Connecting to database...")
conn, cursor = db_connector.dbconnector(namedb, userdb, passworddb, hostdb, portdb, logger)
# Import the provider module

interval, uid, deviceid, user_id, actiontype = None, None, None, None, None
app = FastAPI()




# Create Kafka consumer
conf = {
    'bootstrap.servers': '127.0.0.1:9092',  # Kafka server
    'group.id': 'PTL-Controller-Consumer1',          # Consumer group (must be differnet for different machines)
    'auto.offset.reset': 'latest'         # Start from the earliest message
}

consumer = Consumer(conf)

# Subscribe to the Kafka topic
consumer.subscribe(['PTL-Controller-Topic'])

# Create Kafka Consumer instance

print("Listening for messages...")

# Consume and print messages



async def DataManage(ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, logger, conn, cursor, PTL_IP, PTL_PORT):
    if not controllervalue:
        logger.error("No controllervalue provided.")
        return
    if IsMultiUser == True:
        await combinedata.MultiUserFunction(logger, ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, conn, cursor, PTL_IP, PTL_PORT)
    else:
        await ProcessPTL.PTL_Process(ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, logger, conn, cursor, PTL_IP, PTL_PORT)




async def consume_message():
    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # Wait for a message for 1 second
            if msg is None:
                continue  # No message available, continue polling
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            else:
                headers = dict(msg.headers() or [])
                kafkamachineid = headers.get('machine_id')
                kafkamachine_id= kafkamachineid.decode() if kafkamachineid else None

                if kafkamachine_id == machineid:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{timestamp}] Received message: {msg.value().decode('utf-8')} from {msg.topic()} [{msg.partition()}]")
                    # Deserialize the JSON string into a Python dictionary
                    try:
                        message_data = json.loads(msg.value().decode('utf-8'))
                        #print("Decoded JSON data:", message_data)
                        
                        # Access individual fields from the JSON data
                        ptlcolor = message_data.get('ptlcolor')
                        controllervalue = message_data.get('controllervalue')
                        action = message_data.get('action')
                        display = message_data.get('display')
                        interval = message_data.get('interval')
                        uid = message_data.get('uid')
                        deviceid = message_data.get('deviceid')
                        machine_id = message_data.get('machine_id')
                        user_id = message_data.get('user_id')
                        actiontype = message_data.get('actiontype')
                        await DataManage(ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, logger, conn, cursor, PTL_IP, PTL_PORT)
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")
    
    finally:
        consumer.close()
    
    

def start_uvicorn():
    uvicorn.run(app, host='0.0.0.0', port=9023)

if __name__ == "__main__":
    Thread(target=start_uvicorn).start()
    Thread(target=lambda: asyncio.run(sockets.monitor_connection(PTL_IP, PTL_PORT, logger, conn, cursor))).start()
    if IsMultiUser == True:
        Thread(target=lambda: asyncio.run(combinedata.process_ptl_for_users(logger, interval, uid, deviceid, machineid, user_id, actiontype, conn, cursor, PTL_IP, PTL_PORT))).start()
    Thread(target=lambda: asyncio.run(consume_message())).start() 


