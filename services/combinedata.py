import asyncio
from threading import Thread
import ProcessPTL

map_data = {}
result = {}
combined_result = {}
color1 = "SP"
color2 = "SG"

async def combined_data(ptlcolor):
    global combined_result
    combined_result = {}

    # Loop through map_data to merge controllervalue and display per color
    for ptlcolor, devices in map_data.items():
        controllervalues = []
        displays = []

        # Loop through devices and users to collect values
        for deviceid, users in devices.items():
            for user_id, (controllervalue, display) in users.items():
                controllervalues.append(controllervalue)
                displays.append(display)

        # Store the merged data for each color with correct mapping
        combined_result[ptlcolor] = {
            'controllervalue': ','.join(controllervalues),
            'display': ','.join(displays)
        }

    print("Combined Data: %s", combined_result)
    await compare_combined_data(combined_result)  # Use combined_result, NOT combined_data
    return combined_result

async def compare_combined_data(combined_data):
    global result

    sg_data = combined_data.get(color1)
    sy_data = combined_data.get(color2)
    #print(sg_data)
    #print(sy_data)
    if not sg_data or not sy_data:
        return None, None

    try:
        # Extract controllervalues and display as ordered lists
        sg_values = sg_data['controllervalue'].split(',')
        sg_displays = sg_data['display'].split(',')
        sy_values = sy_data['controllervalue'].split(',')
        sy_displays = sy_data['display'].split(',')

        # Maintain original order by using a list of tuples
        sg_pairs = list(zip(sg_values, sg_displays))  
        sy_pairs = list(zip(sy_values, sy_displays))

        # Convert to ordered dicts for exact mapping
        sg_dict = {cv: display for cv, display in sg_pairs}
        sy_dict = {cv: display for cv, display in sy_pairs}

        # Find common controllervalues (while preserving order)
        common_values = [cv for cv in sg_values if cv in sy_dict]

        if common_values:
            # Construct result while keeping correct mapping
            result[color1] = {
                'controllervalue': ','.join(common_values),
                'display': ','.join(sg_dict[cv] for cv in common_values)
            }

            result[color2] = {
                'controllervalue': ','.join(common_values),
                'display': ','.join(sy_dict[cv] for cv in common_values)
            }

            print("Final Result (first only): %s", result[color1])
            print("Final Result (second only): %s", result[color2])
            return result[color1], result[color2]

    except Exception as e:
        print("Error processing data: %s", e)

    return None, None

async def MultiUserFunction(logger, ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, conn, cursor, PTL_IP, PTL_PORT):
    global map_data
    if interval == 0 and actiontype == "SORT":
        print("HII")
        # Initialize the color and device mappings
        map_data.setdefault(ptlcolor, {}).setdefault(deviceid, {})[user_id] = (controllervalue, display)

    else:
        # Track if the device was found and remove it from map_data
        found = False
        for color, devices in map_data.items():
            if deviceid in devices:
                del devices[deviceid]
                logger.info(f"DeviceID {deviceid} removed from {color}")
                found = True
                # If the color is "SB", update the combined result for this color
                logger.info("Recalculating combined data")
                await combined_data(color)
                #Thread(target=lambda: asyncio.run(combined_data(color))).start()
                break

        if not found:
            logger.warning("DeviceID not found in any color.")

    await ProcessPTL.PTL_Process(ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, logger, conn, cursor, PTL_IP, PTL_PORT)
    await combined_data(ptlcolor)
    
async def process_ptl_for_users(logger, interval, uid, deviceid, machine_id, user_id, actiontype, conn, cursor, PTL_IP, PTL_PORT):
    global client_socket, is_connected, map_data, ptlcolor

    toggle = True  # To alternate between resultsg and resultsy

    while True:
        resultsg, resultsy = await compare_combined_data(combined_result)
        
        if (resultsg and resultsy) is not None:
            if toggle:
                data = resultsg
                ptlcolor = color1
            else:
                data = resultsy
                ptlcolor = color2
            # Alternate between resultsg and resultsy each second
            toggle = not toggle  # Switch on the next loop
            # Extract the controllervalue
            controllervalue = data.get('controllervalue')
            display = data.get('display')
            logger.info("Extracted controllervalue: %s, %s", controllervalue, display)
            action = 'Mix'
            actiontype = ''
            if controllervalue:   
                await ProcessPTL.PTL_Process(ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, logger, conn, cursor, PTL_IP, PTL_PORT)

        await asyncio.sleep(1)  # Ensure non-blocking execution