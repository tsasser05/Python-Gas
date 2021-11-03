# Python-Gas
A daemon that detects if Ethereum network gas prices are "low".

## Installation
git clone the repository into a directory.

## Usage
./python-gas start

./python-gas stop

## Config
The configuration is controlled by $HOME/.gasrc.  This should be preferred since the user's private access
key will be stored here.  Format is TOML.  If .gasrc does not exist, the program will look for "config.toml" in
its current directory.

Four items are required:

* delay = Number of seconds between runs.
* gas = Threshold for alert.
* key = User private key.
* log = Log directory.  Please keep at in /tmp/python-gas for now.

### Example

## TODO

1. Clean up config data structure and pass it around
