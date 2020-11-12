import psycopg2
import socket
from feelings_list import negative_wordlist

def connectToDatabase_pg(cfg):
    pg_db_IPaddress = socket.gethostbyname(cfg['POSTGRES_DATABASE']['pg_db_hostname'])
    conn = psycopg2.connect(
      port=cfg['POSTGRES_DATABASE']['pg_db_port'],
      dbname=cfg['POSTGRES_DATABASE']['pg_db_name'],
      user=cfg['POSTGRES_DATABASE']['pg_db_username'],
      password=cfg['POSTGRES_DATABASE']['pg_db_password'],
      host=pg_db_IPaddress
      # host=pg_db_hostname
                           )
    print("Connection established. Postgres v. {}".format(conn.server_version))
    return conn

def insertChatData_pg(textData, cn, symbol, cfg):
    cursor = cn.cursor()
    selectQuery = """
      SELECT 
        text 
      FROM {} 
      WHERE timestamp >= NOW() - INTERVAL '15 minutes'
      AND text='{}';
                  """.format(cfg['CHANNEL']['pg_tableName'], textData)
    print(selectQuery)
    cursor.execute(selectQuery)
    _ = cursor.fetchone()
    if cursor.rowcount < 1:
        if any(negativeStr in textData for negativeStr in negative_wordlist):
            positivity = 'F'
        else:
            positivity = 'T'
        insertQuery = """
          INSERT INTO {}
          (text, positive, timestamp, ticker_symbol, discord_server, discord_channel)
          VALUES
          ('{}', '{}', NOW(), '{}', '{}', '{}');
                      """.format(
            cfg['CHANNEL']['pg_tableName'],
            textData.strip(),
            positivity,
            symbol,
            cfg['CHANNEL']['discord_name'],
            cfg['CHANNEL']['channel_name']
                                )
        print(insertQuery)
        _ = cursor.execute(insertQuery)
    else:
        print("We already stored this msg")
    cn.commit()
    cursor.close()

