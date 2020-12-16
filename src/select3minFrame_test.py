#!/usr/bin/env python3

import psycopg2
import configparser

class Fakelog: 
    def info(self, txt): 
        print(txt) 
    def error(self, txt): 
        print(txt)
    def debug(self, txt):
    	print(txt)


def connectToDatabase_test(log, port, dbname, user, password, host):
    try:
        conn = psycopg2.connect(port=port,dbname=dbname,user=user,password=password,host=host)
        log.info("Connection established. Postgres v. {}".format(conn.server_version))
    except(psycopg2.OperationalError):
        log.error("Failed once to resolve the DB hostname. Retrying.")
        pg_db_IPaddress = socket.gethostbyname(host)
        conn = psycopg2.connect(port,dbname,user,password,pg_db_IPaddress)
        log.info("Connection established. Postgres v. {}".format(conn.server_version))
    return conn


def select3minChatTest(cn, table, log):
	# This function only works during market hours
    cursor = cn.cursor()
    selectQuery = """
    SELECT text FROM {} WHERE timestamp >= NOW() - INTERVAL '3 minutes';
      """.format(table)
    log.info(selectQuery)
    cursor.execute(selectQuery)
    recents = cursor.fetchall()
    log.debug(str(recents))
    msgs = [r[0].strip() for r in recents]
    return msgs


def findIfAnyExactMatches(chatStringToMatch, dbResults, log):
	s = chatStringToMatch
	anyMatch = False
	for t in dbResults:
		mtch = s == t.strip()
		log.info("{} == {} | Result: {}".format(s, t.strip(), mtch))
		if mtch: log.info("Found a match!")
		anyMatch |= mtch
	return anyMatch


def configure(conffile, logging):
    cf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    cf.read(conffile)
    logging.debug("Loaded config file {}".format(conffile))                                        
    return cf


def run():
	logger = Fakelog()
	conf = configure("/Users/mttpgn/src/discordsentiment/cfgs/ec2/wsb/so.ini", logger)
	c = connectToDatabase_test(
		logger,
		conf['POSTGRES_DATABASE']['pg_db_port'],
		conf['POSTGRES_DATABASE']['pg_db_name'],
		conf['POSTGRES_DATABASE']['pg_db_username'],
		conf['POSTGRES_DATABASE']['pg_db_password'],
		conf['POSTGRES_DATABASE']['pg_db_hostname'])
	recentPulls = select3minChatTest(c, conf['CHANNEL']['pg_tableName'],logger)
	logger.info("Size of pull: {}".format(len(recentPulls)))
	logger.info("First element pulled was: {}".format(recentPulls[0]))
	logger.info("Did we find at least one exact match?\n{}".format(findIfAnyExactMatches("v PLTR on sale", recentPulls, logger)))
	c.close()


if (__name__ == '__main__'):
	run()
