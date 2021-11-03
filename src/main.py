#!/usr/bin/env python3

import requests
import pprint
import toml
import time
import os
import logging
import sys
import atexit
import signal
from pathlib import Path


def summon(pidfile,
           *,
           stdin='/dev/null',
           stdout='/dev/null',
           stderr='/dev/null'):

    if os.path.exists(pidfile):
        raise RuntimeError("Python-Gas is already running")

    # Fork to detach from parent
    try:
        if os.fork() > 0:
            # Parent exit
            raise SystemExit(0)
    except OSError as e:
        raise RuntimeError("First fork failed")

    os.chdir('/')
    os.umask(0)
    os.setsid()

    # Fork again to release session leadership
    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError as e:
        raise RuntimeError('Second fork failed')

    # Clean out IO buffers
    sys.stdout.flush()
    sys.stderr.flush()

    # Replace file descriptors for stdin, stdout, stderr
    with open(stdin, 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(stdout, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open(stderr, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Open and write to PID file
    with open(pidfile, 'w') as f:
        print(os.getpid(), file=f)

    # Delete pid file upon exit or signal
    atexit.register(lambda: os.remove(pidfile))

    # Signals
    def sigterm_handler(signo, frame):
        raise SystemExit(1)

    signal.signal(signal.SIGTERM, sigterm_handler)


'''
gas()

Queries the target URL, parses the results and writes them to the logfile.

The configuration is stored in either ~/.gasrc or the local working directory as config.toml.
Format is TOML.  Four lines are required:

"delay = Number of seconds between runs
"gas" = Average gas threshold
"key" = Private user key from the target URL
"log" = Logging directory.  Default should be /tmp/python-gas/

I am debating about whether or not to have this send email.  It may be better to integrate this into telegram.

'''


def gas():
    # Find the config file and set variables.  ~/.gasrc overrides config.toml.
    home_dir = Path.home()
    rc_file = str(home_dir) + "/.gasrc"

    if os.path.exists(rc_file):
        file_name = rc_file

    elif Path.exists(os.path.join(os.getcwd(), "config.toml")):
        file_name = os.path.join(os.getcwd(), "config.toml")
    else:
        sys.exit("python-gas:  The config file does not exist.  Exiting.")

    print("The config file used is: {}\n".format(file_name))
    f = open(file_name, "r")
    config_data = toml.load(f)
    f.close()

    tags = ["delay", "gas", "key", "log"]

    for tag in tags:
        if tag in tags:
            next
        else:
            sys.stdout.write(
                'Tag {} was not found in the config data.  Check config file to verify all tags are configured.'.format(tag))

    # TBD .. probably need some defaults to get around missing variables in the config file
    # TBD .. figure out how to dynamically create the variable from the tag in the loop above
    gas = config_data["gas"]
    delay = config_data["delay"]
    key = config_data["key"]
    log = config_data["log"]
    # email = config_data["email"]

    # Logging
    log_file = os.path.join(log, "python-gas.log")

    if os.path.isdir(log):
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info("Logging directory exists and starting normal operation.")
    else:
        os.mkdir(log)
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info("Log file created and starting normal operation.")

    url = "https://ethgasstation.info/api/ethgasAPI.json?api-key=" + key

    # Initial run
    req = requests.get(url)

    # Capture the json from request.
    req_json = req.json()

    # Print average gas from the json obs.
    query_result = "Current gas average :" + str(req_json['average'])
    logging.info(query_result)

    # Looping after initial run according to "delay" set in config file
    while(1):
        time.sleep(delay)
        req = requests.get(url)
        req_json = r.json()
        avg_gas = req_json['average']

        if avg_gas <= gas:
            msg = "Alert! Current gas is LOW: " + str(req_json['average'])
            logging.info(msg)
        else:
            alt_msg = "Current gas is not below the threshold."
            logging.info(alt_msg)


def main():
    sys.stdout.write('Daemon started with pid {}\n'.format(os.getpid()))
    while True:
        gas()


if __name__ == '__main__':

    # TBD ...  need to put toml file stuff here to remove hardcoded paths.

    PIDFILE = '/tmp/python-gas/python-gas.pid'

    if len(sys.argv) != 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)

    if sys.argv[1] == 'start':
        try:
            summon(PIDFILE,
                   stdout='/tmp/python-gas/daemon.log',
                   stderr='/tmp/python-gas/error.log')
        except RuntimeError as e:
            print(e, file=sys.stderr)
            raise SystemExit(1)

        main()

    elif sys.argv[1] == 'stop':
        if os.path.exists(PIDFILE):
            with open(PIDFILE) as f:
                os.kill(int(f.read()), signal.SIGTERM)
                sys.stdout.write(
                    'Daemon shut down at {}\n'.format(time.ctime()))
        else:
            print('Process not running', file=sys.stderr)
            raise SystemExit(1)

    else:
        print("Unknown command {!r}".format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)
