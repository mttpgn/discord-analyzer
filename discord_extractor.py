#!/usr/bin/env python3

from datetime import datetime
import time
import pyautogui
import pytesseract as tess
import sqlite3
import os
import re
from PIL import Image
from configs import *

ALL_HOURS_FLAG = True

with open('{}/tickers.txt'.format(projroot)) as tickers:
    rawtickers = tickers.read().split('\n')
    regexfirstpart = '( |^|\$)'
    regexlastpart = '( |$|,|\.|!|\?)'
    tickerregexes = \
      [ (re.compile(
          '{}{}{}'.format(
            regexfirstpart, 
            t, 
            regexlastpart), 
          flags=re.IGNORECASE), 
        t) for t in rawtickers if t != '' ]
    # print(tickerregexes)

with open(dictionary_location) as wordsf:
    words = wordsf.read().split('\n')[10:]

def main():
    while True:
      if datetime.now().hour in list(range(9,16)) or ALL_HOURS_FLAG:
          newestfname = datetime.now().strftime(\
            '{}/%Y%m%d%H%m%S{}'.format(\
            ss_location, \
            exten
                                      )
                                               )
          pyautogui.screenshot(\
            newestfname, \
            region=(\
              ss_left, \
              ss_top, \
              ss_width, \
              ss_height
                   )
                              )
          img = Image.open(newestfname)
          latestChatsPre = tess.image_to_string(img).split('\n')
          latestChats = [t for t in latestChatsPre if '(' not in t and ')' not in t]
          latestChatsCleaned = [ "".join( list( filter(
            lambda x : x in \
              "QWERTYUIOPLKJHGFDSAZXCVBNM,.! qwertyuioplkjhgfdsazxcvbnm1234567890$%*&^", 
            line) ) ) for line in latestChats ]
          # print('\nlatestChatsCleaned\n##################')
          # print(latestChatsCleaned)
          connection = None
          while(connection is None):
              try:
                  connection = connectToDatabase()
              except e:
                  print("Failed to connect: {} ... retrying".format(e))
                  time.sleep(0.01)
          for chatTxt in latestChatsCleaned:
              for tickerre_tup in tickerregexes:
                  if coherencyCheck(chatTxt):
                      if tickerre_tup[0].search(chatTxt) is not None:
                          print('REGEX of \'{}\' recognized msg "{}"'.format(tickerre_tup[0], chatTxt))
                          insertChatData(chatTxt, connection, tickerre_tup[1])
          connection.close()
          time.sleep(5)
          os.remove(newestfname)
          pyautogui.move(-30, 0)
          pyautogui.move(30, 0)
      else:
          print("Sentiment analysis not running outside market hours")
          time.sleep(3600)

def coherencyCheck(phrase):
    if len(phrase) < 9:
        return False
    for phrasew in phrase.split(' '):
        if phrasew.lower() in words:
            return True
    return False

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
    if count.fetchone() is None:
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
