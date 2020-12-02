import psycopg2
import logging
from src.feelings_list import negative_wordlist

def connectToDatabase_pg(cfg, log):
    conn = psycopg2.connect(
      port=cfg['POSTGRES_DATABASE']['pg_db_port'],
      dbname=cfg['POSTGRES_DATABASE']['pg_db_name'],
      user=cfg['POSTGRES_DATABASE']['pg_db_username'],
      password=cfg['POSTGRES_DATABASE']['pg_db_password'],
      host=cfg['POSTGRES_DATABASE']['pg_db_hostname'])
    log.info("Connection established. Postgres v. {}".format(conn.server_version))
    return conn

def insertChatData_pg(textData, cn, symbol, cfg, log):
    cursor = cn.cursor()
    selectQuery = """
      BEGIN;
      SELECT 
        text 
      FROM {} 
      WHERE timestamp >= NOW() - INTERVAL '15 minutes'
      AND text='{}';
      END;
                  """.format(cfg['CHANNEL']['pg_tableName'], textData)
    log.info(selectQuery)
    cursor.execute(selectQuery)
    _ = cursor.fetchone()
    if cursor.rowcount < 1:
        if any(negativeStr in textData for negativeStr in negative_wordlist):
            positivity = 'F'
        else:
            positivity = 'T'
        insertQuery = """
          BEGIN;
          INSERT INTO {}
          (text, positive, timestamp, ticker_symbol, discord_server, discord_channel)
          VALUES
          ('{}', '{}', NOW(), '{}', '{}', '{}');
          END;
                      """.format(
            cfg['CHANNEL']['pg_tableName'],
            textData.strip(),
            positivity,
            symbol,
            cfg['CHANNEL']['discord_name'],
            cfg['CHANNEL']['channel_name']
                                )
        log.info(insertQuery)
        _ = cursor.execute(insertQuery)
    else:
        log.info("We already stored this msg")
    cn.commit()
    cursor.close()

def insertChatDataNoSelect_pg(textData, cn, symbol, cfg, log):
    if any(negativeStr in textData for negativeStr in negative_wordlist):
        positivity = 'F'
    else:
        positivity = 'T'
    cursor = cn.cursor()
    insertQuery = """
          BEGIN;
          INSERT INTO {}
          (text, positive, timestamp, ticker_symbol, discord_server, discord_channel)
          VALUES
          ('{}', '{}', NOW(), '{}', '{}', '{}');
          END;
                      """.format(
        cfg['CHANNEL']['pg_tableName'],
        textData.strip(),
        positivity,
        symbol,
        cfg['CHANNEL']['discord_name'],
        cfg['CHANNEL']['channel_name']
                                )
    log.info(insertQuery)
    _ = cursor.execute(insertQuery)
    cn.commit()
    cursor.close()

