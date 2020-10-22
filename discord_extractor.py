#!/usr/bin/env python3

from datetime import datetime
import time
import pyautogui
import pytesseract as tess
import sqlite3
import os
from PIL import Image
from configs import *

with open('{}/tickers.txt'.format(projroot)) as tickers:
    rawtickers = tickers.read().split('\n')
    tickerforms = [ \
      [ \
        ' {} '.format(t), \
        ' {} '.format(t.lower()), \
        '${} '.format(t), \
        ' {} '.format(t.title()) 
      ] for t in rawtickers if t != ''
                  ]
    numTickerforms = len(tickerforms[0])

def main():
  while True:
    if datetime.now().hour in list(range(9,16)):
      newestfname = datetime.now().strftime(
        '{}/%Y%m%d%H%m%S{}'.format(
          ss_location, 
          exten
                                  )
                                           )
      pyautogui.screenshot(
        newestfname, 
        region=(
          ss_left, 
          ss_top, 
          ss_width, 
          ss_height 
               )
                          )
      img = Image.open(newestfname)
      latestChatsPre = tess.image_to_string(img).split('\n')
      latestChats = [t for t in latestChatsPre if '(' not in t and ')' not in t]
      latestChatsCleaned = ["".join( list( filter(lambda x : x in "QWERTYUIOPLKJHGFDSAZXCVBNM,.! qwertyuioplkjhgfdsazxcvbnm1234567890$%*&^", line) ) ) for line in latestChats]
      # print('\nlatestChatsCleaned\n##################')
      # print(latestChatsCleaned)
      connection = None
      while(connection == None):
        try:
          connection = connectToDatabase()
        except e:
          print("Failed to connect: {} ... retrying".format(e))
          time.sleep(0.01)
      lastDataBatch = []
      thisDataBatch = []
      for chatTxt in latestChatsCleaned:
        for tickerformat in tickerforms:
          for i in range(numTickerforms):
            if tickerformat[i] in chatTxt:
              if chatTxt not in lastDataBatch and chatTxt not in thisDataBatch:
                print(chatTxt)
                insertChatData(chatTxt, connection, tickerformat[0].strip())
                thisDataBatch.append(chatTxt) # To prevent duplicate data entries
      connection.close()
      lastDataBatch = thisDataBatch
      time.sleep(5)
      os.remove(newestfname)
      pyautogui.move(-30, 0)
      pyautogui.move(30, 0)
    else:
      time.sleep(3600)

def connectToDatabase():
  conn = None
  try:
    conn = sqlite3.connect(db_location)
    print(sqlite3.version)
  except Error as e:
    print(e)
  finally:
    return conn

def insertChatData(textData, cn, symbol):
  cursor = cn.cursor()
  selectQuery = """
    SELECT text FROM messages where text='{}' AND timestamp > {};
                """.format(\
      textData, \
      int(time.time()) - 300 \
                          )
  # print(query)
  count = cursor.execute(selectQuery)
  if count.fetchone() == None:
    insertQuery = """
      INSERT INTO messages 
      (text, positive, timestamp, ticker_symbol) 
      VALUES 
      ("{}", "{}", {}, "{}");
                  """.format(\
        textData, \
        not any(negativeStr in textData for negativeStr in negative_wordlist), \
        int(time.time()), \
        symbol \
                            )
    _ = cursor.execute(insertQuery)
  else:
    print("we already stored this msg")
  cn.commit()
  cursor.close()

if __name__ == '__main__':
  main()
