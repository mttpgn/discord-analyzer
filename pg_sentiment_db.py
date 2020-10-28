import psycopg2
import socket
from configs import *

pg_db_IPaddress = socket.gethostbyname(pg_db_hostname)

def connectToDatabase_pg():
    conn = psycopg2.connect(
      port=pg_db_port, 
      dbname=pg_db_name, 
      user=pg_db_username, 
      password=pg_db_password, 
      host=pg_db_IPaddress
      # host=pg_db_hostname
                           )
    print("Connection established. Postgres v. {}".format(conn.server_version))
    return conn

def insertChatData_pg(textData, cn, symbol):
    cursor = cn.cursor()
    selectQuery = """
      SELECT 
        text 
      FROM {} 
      WHERE timestamp >= NOW() - INTERVAL '5 minutes'
      AND text='{}';
                  """.format(pg_tableName, textData)
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
          (text, positive, timestamp, ticker_symbol)
          VALUES
          ('{}', '{}', NOW(), '{}');
                      """.format(
            pg_tableName,
            textData.strip(),
            positivity,
            symbol
                                )
        print(insertQuery)
        _ = cursor.execute(insertQuery)
    else:
        print("We already stored this msg")
    cn.commit()
    cursor.close()

