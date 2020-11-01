#!/usr/bin/env python3

from datetime import datetime
import time
import pyautogui
import pytesseract as tess
import os
import re
import configparser
from PIL import Image
from pg_sentiment_db import *

source = 'laptop'
conf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
conf.read('{}.ini'.format(source))

with open('{}/tickers.txt'.format(conf['ENVIRONMENT']['projroot'])) as tickers:
    rawtickers = tickers.read().split('\n')
    regexfirstpart = '( |^|\$)'
    regexlastpart = '( |$|,|\.|!|\?)'
    tickerregexes = \
      [ (re.compile(\
          '{}{}{}'.format(\
            regexfirstpart, \
            t, \
            regexlastpart), \
          flags=re.IGNORECASE), \
        t) for t in rawtickers if t != '' ]
    # print(tickerregexes)

# dbconnection = connectToDatabase_sqlite()
dbconnection = connectToDatabase_pg()

def main():
    while True:
        if datetime.now().hour in list(range(\
          int(conf['COMMON']['hour_begin']), \
          int(conf['COMMON']['hour_finish']))) or conf['COMMON']['all_hours_flag']:
            newestfname = datetime.now().strftime(\
              '{}/%Y%m%d%H%m%S{}'.format(\
              conf['ENVIRONMENT']['ss_location'], \
              conf['COMMON']['exten'] )        )
            pyautogui.screenshot(\
              newestfname, \
              region=(\
                conf['DESKTOP']['ss_left'], \
                conf['DESKTOP']['ss_top'], \
                conf['DESKTOP']['ss_width'], \
                conf['DESKTOP']['ss_height']
                     )          )
            img = Image.open(newestfname)
            latestChatsPre = tess.image_to_string(img).split('\n')
            latestChats = [t for t in latestChatsPre if '(' not in t and ')' not in t]
            latestChatsCleaned = [ "".join( list( filter(
              lambda x : x in \
                "QWERTYUIOPLKJHGFDSAZXCVBNM,.! qwertyuioplkjhgfdsazxcvbnm1234567890$%*&^", 
              line) ) ) for line in latestChats ]
            connection = dbconnection
            while(connection is None):
                try:
                    connection = connectToDatabase_pg()
                    # connection = connectToDatabase_sqlite()
                except Error as e:
                    print("Failed to connect: {} ... retrying".format(e))
                    time.sleep(0.01)
            for chatTxt in latestChatsCleaned:
                for tickerre_tup in tickerregexes:
                    if coherencyCheck(chatTxt):
                        if tickerre_tup[0].search(chatTxt) is not None:
                            print('REGEX of \'{}\' recognized msg "{}"'.format(tickerre_tup[0], chatTxt))
                            # insertChatData_sqlite(chatTxt, connection, tickerre_tup[1])
                            insertChatData_pg(chatTxt, connection, tickerre_tup[1])
            # connection.close()
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
        if len(phrasew) > 2:
            return True
    return False


if __name__ == '__main__':
    main()
