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
import logging

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
    logging.debug("Loaded config file {}".format(conffile))
    return cf

def main():
    conf = takeConfigs()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(conf['ENVIRONMENT']['logfile'])
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
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
    logger.info("Connecting to database")
    dbconnection = pg_sentiment_db.connectToDatabase_pg(conf, logger)
    while True:
        currhr = datetime.now().hour
        beginhr = int(conf['COMMON']['hour_begin'])
        endhr = int(conf['COMMON']['hour_finish'])
        everyhr = conf['COMMON']['all_hours_flag']
        logger.info("Checking whether current hour {} is in {} or the all hours flag ({}) is set.".format(
          currhr, \
          str(list(range(beginhr, endhr))), \
          everyhr)  )
        if currhr in list(range(beginhr, endhr)) or everyhr:
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
            logger.debug("Saved screenshot to {}".format(newestfname))
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
                    logger.warn("Not database connection found. Making new connection.")
                    connection = pg_sentiment_db.connectToDatabase_pg(conf, logger)
                    # connection = connectToDatabase_sqlite()
                except Error as e:
                    logger.error("Failed to connect: {} ... retrying".format(e))
                    time.sleep(0.01)
            for chatTxt in latestChatsCleaned:
                for tickerre_tup in tickerregexes:
                    if coherencyCheck(chatTxt, logger):
                        if tickerre_tup[0].search(chatTxt) is not None:
                            logger.info('REGEX of \'{}\' recognized msg "{}"'.format(tickerre_tup[0], chatTxt))
                            pg_sentiment_db.insertChatData_pg(chatTxt, connection, tickerre_tup[1], conf, logger)
            # connection.close()
            logger.debug("Deleting screenshot file")
            os.remove(newestfname)
            logger.debug("Jiggling mouse for keepalive")
            pyautogui.moveTo(pyautogui.Point(x=900, y=90))
            pyautogui.move(5, -5)
        else:
            logger.info("Sentiment analysis not running outside market hours")
            time.sleep(3600)

def coherencyCheck(phrase, log):
    if len(phrase) < 9:
        return False
    for phrasew in phrase.split(' '):
        if len(phrasew) > 2:
            return True
    log.info("discarding the following string of letters: {}".format(phrase))
    return False


if __name__ == '__main__':
    main()
