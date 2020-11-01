import psycopg2
import socket
import configparser
from feelings_list import negative_wordlist

source = 'ec2'

conf = configparser.ConfigParser()
conf.read('{}.ini'.format(source))

pg_db_IPaddress = socket.gethostbyname(conf['POSTGRES_DATABASE']['pg_db_hostname'])

def connectToDatabase_pg():
    conn = psycopg2.connect(
      port=conf['POSTGRES_DATABASE']['pg_db_port'], 
      dbname=conf['POSTGRES_DATABASE']['pg_db_name'], 
      user=conf['POSTGRES_DATABASE']['pg_db_username'], 
      password=conf['POSTGRES_DATABASE']['pg_db_password'], 
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
                  """.format(conf['CHANNEL']['pg_tableName'], textData)
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
            conf['CHANNEL']['pg_tableName'],
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

