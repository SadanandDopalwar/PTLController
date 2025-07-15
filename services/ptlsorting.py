
counter = 1
previous_command = ""
previous_counter = ""
previousAction = ""
map_last_command = {}
    
async def formatptldata(action, logger, ptl_array, display, display_array):
    if action in ['Round', 'Combo', 'Single', 'Closebag']:
        logger.info("Checking Action")
        formatted_ptl_array = [f"{int(controllervalue):04d}{display}" for controllervalue in ptl_array]
    elif action == 'Mix':
        #action = mix (like onepharma)
        formatted_ptl_array = [f"{int(ptl_array[i]):04d}{display_array[i]}" for i in range(len(ptl_array))]

        #formatted_ptl_array = [f"{int(ptl_array[i]):04d}{int(display_array[i]):05d}" for i in range(len(ptl_array))]  #for OnePharmacy, pass 4 digit for each ptl
    return formatted_ptl_array
    #formatted_ptl_array = [f"{int(controllervalue):04d}{display}" for controllervalue in ptl_array]
async def update_lastdiffuse(logger, cursor, conn, ptl_data1, deviceid, user_id):
    try:
        logger.info("Updating Last Diffuse Command")
        cursor.execute("UPDATE ptl_user SET lastdiffusecommand = %s WHERE deviceid = %s AND user_id = %s", (ptl_data1, deviceid, user_id))
        conn.commit()
    except Exception as e:
        logger.error("Error updating last diffuse command: %s", str(e))


async def select_last_diffuse(logger, cursor, conn, deviceid, user_id):
    try:
        ptl_array_demo = map_last_command[deviceid][user_id]
        # cursor.execute("SELECT lastdiffusecommand FROM ptl_user WHERE deviceid = %s AND user_id = %s", (deviceid, user_id,))
        # ptl_array_demo = cursor.fetchone()[0]
        return ptl_array_demo
    except Exception as e:
        logger.error("Error selecting last diffuse command: %s", str(e))
        return None
async def get_command(uid, controllervalue, color, display, deviceid, conn, cursor, logger, action, user_id, actiontype):
    global counter, previous_command, previousAction, map_last_command
    diffuse_command = None
    diffuse_command1 = None
    formatcolor = color
    counter = (counter % 999) + 1
    formatted_regular = (counter * 3 - 2) % 1000
    formatted_diffuse = (counter * 3 - 1) % 1000
    formatted_intdiffuse = (counter * 3) % 1000
     
    formatted_counter_regular = f"{formatted_regular:03d}"
    formatted_counter_diffuse = f"{formatted_diffuse:03d}"
    formatted_interval_diffuse = f"{formatted_intdiffuse:03d}"
     

    ptl_array = str(controllervalue).split(',')
    logger.info("ptl array: %s", ptl_array)
    ptl_format = ''.join(ptl_array)
    display_array = display.split(',')
    logger.info("display array: %s", display_array)
    formatted_ptl_array = await formatptldata(action, logger, ptl_array, display, display_array)
    # if (action == 'Round' or action == 'Combo' or action == 'Single' or action == 'Closebag'):
    #     logger.info("Checking Action")
    #     formatted_ptl_array = [f"{int(controllervalue):04d}{display}" for controllervalue in ptl_array]
    # else:
    #     #action = mix (like onepharma)
    #     formatted_ptl_array = [f"{int(ptl_array[i]):04d}{int(display_array[i]):05d}" for i in range(len(ptl_array))]  #for OnePharmacy, pass 4 digit for each ptl
    # #formatted_ptl_array = [f"{int(controllervalue):04d}{display}" for controllervalue in ptl_array]
    
    logger.info("Formatting PTL Address Array: %s", formatted_ptl_array)
    formatted_ptl_address_array = ''.join(formatted_ptl_array)
    formattedptladdressarray = formatted_ptl_address_array
    logger.info("Formatting PTL Address: %s, %s", formatcolor, formattedptladdressarray)
    ptl_command1 = 'PP5050000m1' + formatcolor + formattedptladdressarray
    ptl_length = len(ptl_command1)
    formatted_ptl_length = f"{ptl_length:04d}"
    formattedptllength = formatted_ptl_length

    regular_command = formatted_counter_regular + formattedptllength + ptl_command1
    
    # Create a diffuse command of the previous regular command if there is a previous command

    
    
    if (action == 'Round' or action == 'Combo'):
        ptl_format1 = ''.join(ptl_array)
        logger.info("ptl_format1: %s", ptl_format1)
        format_ptl = ptl_format1
        ptl_command2 = 'D' + format_ptl
        ptl_length = len(ptl_command2)
        formattedptllength = f"{ptl_length:04d}"
        logger.info("Format: %s",formattedptllength)
        diffuse_command1 = formatted_interval_diffuse + formattedptllength + ptl_command2
        logger.info("Made Diffuse Command")
     
        if action == 'Round' and previousAction == 'Single':
            logger.info("Action is Round and Previous Action is Single")
            ptl_array_demo = await select_last_diffuse(logger, cursor, conn, deviceid, user_id)
            if ptl_array_demo is not None:
                logger.info("Last Diffuse Command: %s", ptl_array_demo)
                ptl_format2 = ''.join(ptl_array_demo)
                print("ptl_format:", ptl_format2)


                #ptl_format1 = ''.join(previous_command)
                logger.info("ptl_format2: %s", ptl_format2)
                
                format_ptl2 = ptl_format2
                ptl_command2 = 'D' + format_ptl2
                ptl_length2 = len(ptl_command2)
                formatted_ptl_length2 = f"{ptl_length2:04d}"
                formattedptllength2 = formatted_ptl_length2

                diffuse_command = formatted_counter_diffuse + formattedptllength2 + ptl_command2
            
    if previous_command and previousAction != 'Round' and ((action == 'Single') or action == 'Combo'): # previous and current type not = bagging
        logger.info("Action is Single")
        # ptl_array_demo = map_last_command[deviceid]
        # print(ptl_array_demo)
        # cursor.execute("SELECT lastdiffusecommand FROM devices WHERE deviceid = %s", (deviceid,))
        # ptl_array_demo = cursor.fetchone()[0]
        ptl_array_demo = await select_last_diffuse(logger, cursor, conn, deviceid, user_id)
        if ptl_array_demo is not None:
            logger.info("Last Diffuse Command: %s", ptl_array_demo)
            ptl_format2 = ''.join(ptl_array_demo)
            print("ptl_format:", ptl_format2)


            #ptl_format1 = ''.join(previous_command)
            logger.info("ptl_format2: %s", ptl_format2)
            
            format_ptl2 = ptl_format2
            ptl_command2 = 'D' + format_ptl2
            ptl_length2 = len(ptl_command2)
            formatted_ptl_length2 = f"{ptl_length2:04d}"
            formattedptllength2 = formatted_ptl_length2

            diffuse_command = formatted_counter_diffuse + formattedptllength2 + ptl_command2
        

    


    
    # Store the current controllervalue as the previous command for the next iteration
    previous_command = ptl_array
    previousAction = action
    ptl_data1 = ''.join(previous_command)
    logger.info("PTL DATA: %s", ptl_data1)
    #print(deviceid)
    #closebag n delink process
    logger.info("Action: %s", action)
    if not (action == 'Closebag' and previousAction == 'Round'):
        if deviceid not in map_last_command:
            map_last_command[deviceid] = {}  # Ensure deviceid key exists
        
        map_last_command[deviceid][user_id] = ptl_data1
        #print(map_last_command)
        #await update_lastdiffuse(logger, cursor, conn, ptl_data1, deviceid, user_id)
    
    if diffuse_command:
        return diffuse_command, regular_command, diffuse_command1
    else:
        return None, regular_command, diffuse_command1

