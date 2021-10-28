import requests
import pprint
import toml
import time
import os
import logging
import sys


# Read the config.toml file and set variables
file_name = os.path.join(os.getcwd(), "config.toml")

if os.path.exists(file_name):
    f = open(file_name, "r")
    config_data = toml.load(f)
    f.close()
    # TBD .. convert to processing function
    gas = config_data["gas"]
    delay = config_data["delay"]
    key = config_data["key"]
    log = config_data["log"]
else:
    sys.exit("python-gas:  The config file does not exist.  Exiting.")

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
r = requests.get(url)

# Capture the json from request.
x = r.json()

# Print average gas from the json obs.
query_result = "Current gas average :" + str(x['average'])
print(query_result)
logging.info(query_result)

while(1):
    time.sleep(delay)

    r = requests.get(url)
    x = r.json()
    avg_gas = x['average']
    if avg_gas <= gas:
        msg = "Alert! Current gas is LOW: " + str(x['average'])
        print(msg)
        logging.info(msg)
    else:
        alt_msg = "Current gas is not below the threshold."
        print(alt_msg)
        logging.info(alt_msg)
