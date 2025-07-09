import psycopg2

def dbconnector(namedb, userdb, passworddb, hostdb, portdb, logger):
    logger.info("Connecting to database...")
    try:
        conn = psycopg2.connect(
        dbname=namedb,
        user=userdb,
        password=passworddb,
        host=hostdb,
        port=portdb
        )
        cursor = conn.cursor()
        logger.info("Database Connected Successfully...")
        return conn, cursor
    except:
        logger.error("Error while connecting to Database")
        return None, None   