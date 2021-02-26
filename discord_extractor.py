#!/usr/bin/env python3

from datetime import datetime
import time
import pyautogui
import pytesseract as tess
import os
import re
import configparser
from PIL import Image
import src.pg_sentiment_db as pg_sentiment_db
import sys
import logging
import distutils.util
import requests
from psycopg2 import DatabaseError, InterfaceError, ProgrammingError
from Levenshtein import distance
from src.clearlogs import clearlogs

pyautogui.FAILSAFE = False
stddev = 1 - 0.682

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
    if conffile[:5] == 'cfgs/':
        conffile = conffile[5:]
    understandconfigfile(sys.argv[1])
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
        log.error(\
            "Received {} status code.".format(r.status_code))
        raise Exception(\
            "Please check if gist.github.com is accessible.")
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
    if len(phrase) < 5:
        return False
    for phrasew in phrase.split(' '):
        if len(phrasew) > 2:
            return True
    return False

def noopLoop(configuration, log):
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
        logger.info(("Checking if current hour {} is in {} or the all-" + \
         "hours flag ({}) is set.").format( \
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
            latestChats = \
              [t for t in latestChatsPre if '(' not in t and ')' not in t]
            latestChatsCleaned = [ "".join( list( filter(
              lambda x : x in \
                "QWERTYUIOPLKJHGFDSAZXCVBNM,.! " + \
                "qwertyuioplkjhgfdsazxcvbnm" + \
                "1234567890$%*&^", 
              line) ) ).strip() for line in latestChats ]
            connection = dbconnection
            while(connection is None):
                try:
                    logger.warn("No database connection found. " + \
                        "Making new connection.")
                    connection = pg_sentiment_db.connectToDatabase_pg(\
                        conf, logger)
                except Error as e:
                    logger.error(\
                        "Failed to connect: {} ...retrying after 0.1 seconds".format(\
                        e))
                    time.sleep(0.1)
            try:
                existingMsgs = pg_sentiment_db.selectChatDataMinsBack(
                    connection,
                    conf,
                    logger)
            except(InterfaceError) as interfaceEx:
                logger.error("{}".format(interfaceEx))
                logger.error(
                    "Connection expired, " + \
                    "attempting to resetablish")
                connection = \
                pg_sentiment_db.connectToDatabase_pg(
                    conf,
                    logger)
                try:
                    existingMsgs = pg_sentiment_db.selectChatDataMinsBack(
                        connection,
                        conf,
                        logger)
                except(ProgrammingError) as progEx:
                    logger.error("{}".format(progEx))
                    logger.warn(
                        "No data found from minutes ago")
                    existingMsgs = []
            except(ProgrammingError) as progEx2:
                logger.error("{}".format(progEx2))
                logger.warn(\
                    "No data found from minutes ago")
                existingMsgs = []
            except(DatabaseError) as dEx:
                logger.error("{}".format(dEx))
                connection.close()
                connection = \
                pg_sentiment_db.connectToDatabase_pg(
                    conf,
                    logger)
                existingMsgs = pg_sentiment_db.selectChatDataMinsBack(
                    connection,
                    conf,
                    logger)
            logger.info(f"Found {len(existingMsgs)} total recent messages.")
            for chatTxt in latestChatsCleaned: # for every sentence detected in the image
                for tickerre_tup in tickerregexes: # for all ticker symbols
                    if coherencyCheck(chatTxt, logger): # proceed for non-garbage
                        if tickerre_tup[0].search(chatTxt) is not None: # Ticker found
                            logger.info(('REGEX of \'{}\' recognized msg ' + \
                             '"{}"').format(tickerre_tup[0], chatTxt))
                            matchFound = False # it's good if a match isn't found
                            k = 0
                            while ((not matchFound) and (k < len(existingMsgs))):
                                n = existingMsgs[k][0]
                                ldist = distance(chatTxt, n)
                                matchFound |= (ldist < (stddev * min(len(chatTxt), len(n))))
                                k += 1
                            if not matchFound:
                                pg_sentiment_db.insertChatDataNoSelect_pg(
                                  chatTxt,
                                  connection,
                                  tickerre_tup[1],
                                  conf,
                                  logger)
            logger.debug("Deleting screenshot file")
            os.remove(newestfname)
            logger.debug("Jiggling mouse for keepalive")
            pyautogui.moveTo(pyautogui.Point(x=conf['DESKTOP']['x_home'], y=conf['DESKTOP']['y_home']))
            pyautogui.move(5, -5)
        else:
            dbconnection.close()
            clearlogs(conf)
            noopLoop(conf, logger)


if __name__ == '__main__':
    main()
