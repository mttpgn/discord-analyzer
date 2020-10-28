import psycopg2
from configs import *

def connectToDatabase_pg():
    conn = psycopg.connect(dbname=pg_db_name, user=pg_db_username, host=pg_db_hostname)
    print("Connection established. Postgres v. {}".format(conn.server_version))
    return conn

def insertChatData_pg(textData, cn, symbol):
    cursor = cn.cursor()
    selectQuery = """
      SELECT text FROM messages where text='{}' AND timestamp > {};
                  """.format(
        textData,
        int(time.time()) - 300
                            )
    print(selectQuery)
    count = cursor.execute(selectQuery)
    if count.fetchone() is None:
        insertQuery = """
          INSERT INTO messages
          (text, positive, timestamp, ticker_symbol)
          VALUES
          ("{}", "{}", {}, "{}");
                      """.format(
          textData,
          not any(negativeStr in textData for negativeStr in negative_wordlist),
          int(time.time()),
          symbol
                                )
        print(insertQuery)
        _ = cursor.execute(insertQuery)
    else:
        print("we already stored this msg")
    cn.commit()
    cursor.close()

