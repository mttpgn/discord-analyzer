import psycopg2
import logging
import socket
import time
from src.feelings_list import negative_wordlist

def connectToDatabase_pg(cfg, log):
    try:
        conn = psycopg2.connect(
          port=cfg['POSTGRES_DATABASE']['pg_db_port'],
          dbname=cfg['POSTGRES_DATABASE']['pg_db_name'],
          user=cfg['POSTGRES_DATABASE']['pg_db_username'],
          password=cfg['POSTGRES_DATABASE']['pg_db_password'],
          host=cfg['POSTGRES_DATABASE']['pg_db_hostname'])
        log.info("Connection established. Postgres v. {}".format(conn.server_version))
    except(psycopg2.OperationalError):
        time.sleep(15)
        log.error("Failed once to resolve the DB hostname. Retrying.")
        pg_db_IPaddress = socket.gethostbyname(cfg['POSTGRES_DATABASE']['pg_db_hostname'])
        conn = psycopg2.connect(
          port=cfg['POSTGRES_DATABASE']['pg_db_port'],
          dbname=cfg['POSTGRES_DATABASE']['pg_db_name'],
          user=cfg['POSTGRES_DATABASE']['pg_db_username'],
          password=cfg['POSTGRES_DATABASE']['pg_db_password'],
          host=pg_db_IPaddress)
        log.info("Connection established. Postgres v. {}".format(conn.server_version))
    return conn

def selectChatDataMinsBack(cn, cfg, log):
    cursor = cn.cursor()
    selectQuery = """
      SELECT
        text
      FROM {}
      WHERE "timestamp" > (NOW() - INTERVAL '{} minutes');
                  """.format(
        cfg['CHANNEL']['pg_tableName'],
        cfg['CHANNEL']['dup_chk_window'])
    log.info(selectQuery)
    cursor.execute(selectQuery)
    recents = cursor.fetchall()
    msgs = [r[0].strip() for r in recents]
    cursor.close()
    return recents

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

