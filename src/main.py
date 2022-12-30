"""Encountered an error reminder

If we encounter another error: "ImportError: cannot import name 'getargspec' from 'inspect'"
Do this:
	- go to ...lib/python3.11/site-packages/parsimonious/expressions.py
	- change line 9 to import getfullargspec

"""

from settings import config # contains our env variables
from web3 import Web3, HTTPProvider
import json

# Initializing the provider and connecting to the chain
provider = HTTPProvider(config["RPC_URL"])
web3 = Web3(provider)
assert web3.isConnected(), "Failed to connect to Web3."
print("Connection to Web3 is a success!")

# Vars for wallet address and wallet's private key
wallet_address = config["WALLET_ADDRESS"]
private_key = config["PRIVATE_KEY"]

# Native token balance
balance = web3.eth.get_balance(wallet_address)
readable_balance = web3.fromWei(balance, "ether")


# Gas fee check
assert readable_balance > 0.5, "Please top up your wallet's native token balance."

# Initializing the pool contract
# axlUSDC/USDC Pool in Polygon Curve.fi
pool_address = config["CURVE_POOL_CONTRACT"]

# Opening the abi json file
with open("abis/curve_axlusdc_usdc_abi.json", "r") as file1:
	abi_pool = json.load(file1)

pool = web3.eth.contract(address=pool_address, abi=abi_pool)
print(f"Connection to { pool.functions.name().call() } is a success!")

# Decimals used in the pool
decimals = pool.functions.decimals().call()