from threading import Thread
import subprocess
import socket
import asyncio
is_connected = False
client_socket = None  # Initial socket state

async def ping(host, PTL_PORT, logger):
    try:
        # Use the subprocess.run method to execute the ping command ["ping", "-c", "1", host],
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Ensures output is returned as a string
            check=True,  # Raises CalledProcessError if the command fails
        )
        return result.returncode == 0
    except Exception as e:
        logger.error("An error occurred: %s", e)
        return False


async def connect_ptl_controller(PTL_IP, PTL_PORT, logger):
    global client_socket, is_connected
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(1.0)  # Set 1-second timeout for connect
        client_socket.connect((PTL_IP, PTL_PORT))
        client_socket.settimeout(None)  # Optional: remove timeout after connect
        if client_socket:
            logger.info(f"Connected to {PTL_IP}:{PTL_PORT}")
            is_connected = True
            return client_socket, is_connected
        else:
            logger.error(f"Failed to connect to {PTL_IP}:{PTL_PORT}")
            is_connected = False
            return None, False
    except socket.error as e:
        logger.error(f"Failed to connect to {PTL_IP}:{PTL_PORT}: {e}")
        is_connected = False
        return None, False
    

async def process_received_data(client_socket, logger, PTL_IP, PTL_PORT):
    global is_connected
    try:
        while True:
            received_data = client_socket.recv(1024)
            received_data1 = received_data.decode()
            logger.info("Received data: %s", received_data1)
            if "t" in received_data1:
                counter = received_data[1:4]
                confirm = received_data[4:9]
                loc_code = received_data[9:13]
                logger.info("Counter, Confirm, Location Code: %s, %s, %s", counter, confirm, loc_code)
                command = b'\x02' + counter + b'0001O\x03'
                logger.info("Command: %s", command)
                client_socket.sendall(command)
            
            if "7t" in received_data1:
                loc_code_str = loc_code.decode('utf-8')  # Assuming utf-8 encoding
                logger.info("Confirmed Location: %s", loc_code_str)
                loc_code_int = int(loc_code_str)
            if "14t" in received_data1:
                newquantity = received_data[17:21]
                # logger.info(f"Counter: {counter}, Confirm: {confirm}, Location Code: {loc_code}")
                # logger.info(f"newquantity: {newquantity}")
                
            else:
                await asyncio.sleep(1)  # Small delay to prevent busy-waiting
    except Exception as e:
        logger.error(f"Unexpected error in process received_data: {e}")
        if client_socket:
            client_socket.close()
        is_connected = False
        await connect_ptl_controller(PTL_IP, PTL_PORT, logger)


async def process_data(regular_command, diffuse_command, diffuse_command1, display, interval, uid, logger, PTL_IP, PTL_PORT):
    global client_socket, is_connected
    if client_socket is not None:
        try:
            if diffuse_command is not None:
                logger.info("Sending Diffuse Command for UID: %s, %s", uid, diffuse_command)
                diff = diffuse_command.encode('utf-8')
                diff_data = b'\x02' + diff + b'\x03'
                client_socket.sendall(diff_data)
                Thread(target=lambda: asyncio.run(process_received_data(client_socket, logger, PTL_IP, PTL_PORT))).start()
            
            if regular_command is not None:
                logger.info("Sending Regular Command for UID: %s, %s", uid, regular_command)
                regular = regular_command.encode('utf-8')
                regular_data = b'\x02' + regular + b'\x03'
                client_socket.sendall(regular_data)
                Thread(target=lambda: asyncio.run(process_received_data(client_socket, logger, PTL_IP, PTL_PORT))).start()
                
            
            if diffuse_command1:
                logger.info("Sending Diffuse Command1 for UID: %s, %s", uid, diffuse_command1)
                await asyncio.sleep(interval)
                diffuse = diffuse_command1.encode('utf-8')
                diffuse_data1 = b'\x02' + diffuse  + b'\x03'
                client_socket.sendall(diffuse_data1)
                Thread(target=lambda: asyncio.run(process_received_data(client_socket, logger, PTL_IP, PTL_PORT))).start()
                return

        
        except Exception as e:
            logger.error(f"Unexpected error in process_data: {e}")
            if client_socket:
                client_socket.close()
            is_connected = False
            await connect_ptl_controller(PTL_IP, PTL_PORT, logger)
    else:
        logger.info("Socket is None, attempting to reconnect...")
        await connect_ptl_controller(PTL_IP, PTL_PORT, logger)

async def UpdateAlarm(is_connected, logger, conn, cursor):
    try:
        israise = not is_connected
        print(is_connected)
        cursor.execute(
            "UPDATE alarms SET isactive = %s WHERE alarmcode = %s AND isactive = %s;",
            (israise, 'IT-7001', is_connected)
        )
        
        conn.commit()
        logger.info(f"Alarm status updated to {israise} in database")
    except Exception as e:
        logger.error(f"Failed to update alarm status in database: {e}")

last_is_connected = None
async def monitor_connection(PTL_IP, PTL_PORT, logger, conn, cursor):
    global client_socket, is_connected, last_is_connected
    while True:
        if is_connected:
            # If connected, just monitor by pinging the IP
            if not await ping(PTL_IP, PTL_PORT, logger):
                logger.warning(f"Connection to {PTL_IP} lost, closing socket...")
                client_socket.close()
                client_socket = None
                is_connected = False
            else:
                logger.info(f"Connection to {PTL_IP} is healthy")
        else:
            # If not connected, attempt to reconnect
            logger.info(f"Attempting to reconnect to {PTL_IP}:{PTL_PORT}...")
            client_socket, is_connected = await connect_ptl_controller(PTL_IP, PTL_PORT, logger)
            if not is_connected:
                logger.info(f"Waiting before retrying...")
                await asyncio.sleep(0.1)  # Wait before next reconnection attempt
            else:
                logger.info(f"Successfully reconnected to {PTL_IP}:{PTL_PORT}")
        # 🔁 Update alarm only if state changed
        if is_connected != last_is_connected:
            await UpdateAlarm(is_connected, logger, conn, cursor)
            last_is_connected = is_connected
        await asyncio.sleep(2)  # Check connection every 2 seconds
