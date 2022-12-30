"""Encountered an error reminder

If we encounter another error: "ImportError: cannot import name 'getargspec' from 'inspect'"
Do this:
	- go to ...lib/python3.11/site-packages/parsimonious/expressions.py
	- change line 9 to import getfullargspec

"""

from decimal import Decimal
from settings import config # contains our env variables
from web3 import Web3, HTTPProvider
import json

# Initializing the provider and connecting to the chain
provider = HTTPProvider(config["RPC_URL"])
web3 = Web3(provider)
assert web3.isConnected(), "Failed to connect to Web3."

# Vars for wallet address and wallet's private key
wallet_address = config["WALLET_ADDRESS"]
private_key = config["PRIVATE_KEY"]

# Native token balance
balance = web3.eth.get_balance(wallet_address)
print(balance)