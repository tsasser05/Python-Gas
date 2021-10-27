import requests
import pprint
import toml
import time

# Read the config.toml file and set variables
f = open("/Users/tom/git/Python-Gas/src/config.toml", "r")
config_data = toml.load(f)
f.close()

gas = config_data["gas"]
delay = config_data["delay"]
key = config_data["key"]

# Request with EthGasStation API key.
# You will need to create an account and input key in the string below.
url = "https://ethgasstation.info/api/ethgasAPI.json?api-key=" + key
r = requests.get(url)

# Capture the json from request.
x = r.json()
# Print average gas from the json obs.
print("Current gas average :" + str(x['average']))

# TODO
# Define criteria for which the script will run in the background
# Every hour? Every 30 minuets? Every 15 minuets?
# This will help determine if this should run as daemon, a job or
# be ran via executable.
# Configure while loop below to accomodate for how this script will be ran.


# This is an infinite loop. It will continuously execute in it's current form
# unless configured otherwise.
while(1):
    time.sleep(delay)

    r = requests.get(url)
    x = r.json()
    gas = x['average']
    if gas <= gas:
        print("Alert! Curent gas is LOW: " + str(x['average']))
