#!/usr/bin/env python3

import datetime
import os
import configparser
import sys
import subprocess

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
    return cf

def clearlogs(cf):
    previousBusinessDay = datetime.datetime.today()
    shift = datetime.timedelta(max(1,(previousBusinessDay.weekday() + 6) % 7 - 3))
    previousBusinessDay = previousBusinessDay - shift
    currentBusinessDay = datetime.datetime.today()
    logdir = "{}/log/".format(cf['ENVIRONMENT']['projroot'])
    today = str(currentBusinessDay).split(' ')[0]
    yday = str(previousBusinessDay).split(' ')[0]
    _ = subprocess.getoutput("cd {} && ls | grep -E -v \"{}|{}\" | xargs rm -f -v && cd - 1>/dev/null".format(logdir, today, yday))

if __name__ == '__main__':
    conf = takeConfigs()
    clearlogs(conf)
