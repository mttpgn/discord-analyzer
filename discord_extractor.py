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
import distutils.util
import requests
from psycopg2 import InterfaceError

pyautogui.FAILSAFE = False

def understandconfigfile(word):
    if '.ini' in word:
        return word
    else:
        return word + '.ini'

def takeConfigs():
    if len(sys.argv) < 2:
        print("Provide the config file as the 1st CLI argument please.")
        exit()
    conffile = understandconfigfile(sys.argv[1])
    if not os.path.exists("cfgs/{}".format(conffile)):
        print("Not a valid filepath: cfgs/{}.".format(conffile))
        exit()
    cf = configparser.ConfigParser(\
      interpolation=configparser.ExtendedInterpolation())
    cf.read("cfgs/{}".format(conffile))
    logging.debug("Loaded config file cfgs/{}".format(conffile))
    return cf

def setUpLogging(configuration):
    logsetup = logging.getLogger(__name__)
    logsetup.setLevel(logging.DEBUG)
    fh = logging.FileHandler(\
      "{}/{}.{}.log".format(\
        configuration['ENVIRONMENT']['projroot'],\
        configuration['ENVIRONMENT']['logfile'], \
        str(datetime.now()).split(' ')[0]\
                           ))
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    fh.setFormatter(formatter)
    logsetup.addHandler(fh)
    return logsetup

def gistPull(url):
    r = requests.get(url)
    if r.status_code == 200:
        symbollist = set(r.text.split('\n'))
    else:
        log.error("Received {} status code.".format(r.status_code))
        raise Exception("Please check whether gist.github.com is accessible.")
    return symbollist

def getTickers(configuration, log):
    tickerlisturl = configuration['DATA']['tickerlisturl']
    blacklisturl = configuration['DATA']['blacklisturl']
    log.info("Pulling ticker list from {}".format(tickerlisturl))
    rawtickers = set(gistPull(tickerlisturl))
    log.info("Pulling blacklist from {}".format(blacklisturl))
    blacklist = set(gistPull(blacklisturl))
    return list(rawtickers - blacklist)

def setupregex(configuration, log):
    tickerlist = getTickers(configuration, log)
    regexfirstpart = '( |^|\$)'
    regexlastpart = '( |$|,|\.|-|!|\?)'
    tregexes = \
      [ (re.compile(\
          '{}{}{}'.format(\
            regexfirstpart, \
            t, \
            regexlastpart), \
          flags=re.IGNORECASE), \
        t) for t in tickerlist if t != '' ]
    return tregexes

def coherencyCheck(phrase, log):
    if len(phrase) < 9:
        return False
    for phrasew in phrase.split(' '):
        if len(phrasew) > 2:
            return True
    log.info("discarding the following string of letters: {}".format(phrase))
    return False

def loop(configuration, log):
    log.info("Sentiment analysis not running outside market hours")
    time.sleep(300)
    log = setUpLogging(configuration)

def main():
    conf = takeConfigs()
    logger = setUpLogging(conf)
    tickerregexes = setupregex(conf, logger)
    logger.info("Connecting to database initially")
    dbconnection = pg_sentiment_db.connectToDatabase_pg(conf, logger)
    while True:
        currhr = datetime.now().hour
        currmin = datetime.now().minute
        currsec = datetime.now().second
        beginhr = int(conf['COMMON']['hour_begin'])
        endhr = int(conf['COMMON']['hour_finish'])
        everyhr = distutils.util.strtobool(conf['COMMON']['all_hours_flag'])
        logger.info("Checking whether current hour {} is in {} or the all hours flag ({}) is set.".format(
          currhr, \
          str(list(range(beginhr, endhr))), \
          everyhr)  )
        if (currhr in list(range(beginhr, endhr)) or everyhr):
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
                    logger.warn("No database connection found. Making new connection.")
                    connection = pg_sentiment_db.connectToDatabase_pg(conf, logger)
                except Error as e:
                    logger.error("Failed to connect: {} ... retrying".format(e))
                    time.sleep(0.1)
            for chatTxt in latestChatsCleaned:
                for tickerre_tup in tickerregexes:
                    if coherencyCheck(chatTxt, logger):
                        if tickerre_tup[0].search(chatTxt) is not None:
                            logger.info('REGEX of \'{}\' recognized msg "{}"'.format(tickerre_tup[0], chatTxt))
                            try:
                                pg_sentiment_db.insertChatData_pg(chatTxt, connection, tickerre_tup[1], conf, logger)
                            except(psycopg2.InterfaceError):
                                logger.error("Connection expired, attempting to resetablish")
                                connection = pg_sentiment_db.connectToDatabase_pg(conf, logger)
                                pg_sentiment_db.insertChatData_pg(chatTxt, connection, tickerre_tup[1], conf, logger)
            logger.debug("Deleting screenshot file")
            os.remove(newestfname)
            logger.debug("Jiggling mouse for keepalive")
            pyautogui.moveTo(pyautogui.Point(x=900, y=90))
            pyautogui.move(5, -5)
        else:
            dbconnection.close()
            loop(conf, logger)


if __name__ == '__main__':
    main()
