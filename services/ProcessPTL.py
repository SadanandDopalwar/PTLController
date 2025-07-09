import GetColor
import ptlsorting
import sockets
import asyncio
from threading import Thread

async def PTL_Process(ptlcolor, controllervalue, action, display, interval, uid, deviceid, machine_id, user_id, actiontype, logger, conn, cursor, PTL_IP, PTL_PORT):
    logger.info("PTL Color: %s", ptlcolor)
    color = await GetColor.colormap(user_id, ptlcolor)
    diffuse_command, regular_command, diffuse_command1 = await ptlsorting.get_command(uid, controllervalue, color, display, deviceid, conn, cursor, logger, action, user_id, actiontype)
    Thread(target=lambda: asyncio.run(sockets.process_data(regular_command, diffuse_command, diffuse_command1, display, interval, uid, logger, PTL_IP, PTL_PORT))).start()
    