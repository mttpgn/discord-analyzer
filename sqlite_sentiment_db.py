import sqlite3
import time
from configs import *

def connectToDatabase_sqlite():
    conn = None
    try:
        conn = sqlite3.connect(db_location)
        print("Connection established. Sqlite version {}".format(sqlite3.version))
    except Error as e:
        print(e)
    finally:
        return conn

def insertChatData_sqlite(textData, cn, symbol):
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

