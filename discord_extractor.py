#!/usr/bin/env python3

from datetime import datetime
import time
import pyautogui
import pytesseract as tess
import os
import re
import configparser
from PIL import Image
import pg_sentiment_db
import sys

pyautogui.FAILSAFE = False

def takeConfigs():
    if len(sys.argv) < 2:
        print("Provide the config file as the 1st CLI argument please.")
        exit()
    conffile = sys.argv[1]
    if not os.path.exists(conffile):
        print("Not a valid filepath: {}.".printf(conffile))
        exit()
    cf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    cf.read(conffile)
    return cf

def main():
    conf = takeConfigs()
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
    dbconnection = pg_sentiment_db.connectToDatabase_pg(conf)
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
                    connection = pg_sentiment_db.connectToDatabase_pg(conf)
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
                            pg_sentiment_db.insertChatData_pg(chatTxt, connection, tickerre_tup[1], conf)
            # connection.close()
            os.remove(newestfname)
            pyautogui.moveTo(pyautogui.Point(x=900, y=90))
            pyautogui.move(5, -5)
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
