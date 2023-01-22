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

chain_id = web3.eth.chain_id
wallet_nonce = web3.eth.getTransactionCount(wallet_address)

# Native token balance and gas fee check
balance = web3.eth.get_balance(wallet_address)
readable_balance = web3.fromWei(balance, "ether")
assert readable_balance > 0.5, "Please top up your wallet's native token balance."


# Initializing the pool contract
# Opening the pool abi json file
with open("abis/curve_axlusdc_usdc_abi.json", "r") as file1:
	abi_pool = json.load(file1)

# axlUSDC/USDC Pool in Polygon Curve.fi
pool_address = config["CURVE_POOL_CONTRACT"]

pool = web3.eth.contract(address=pool_address, abi=abi_pool)
print(f"Connection to { pool.functions.name().call() } is a success!")


# Opening the erc20 abi json file
with open("abis/erc20_abi.json", "r") as file2:
	abi_erc20 = json.load(file2)

# Initializing the USDC contract
usdc_address = config["USDC_CONTRACT"]
usdc = web3.eth.contract(address=usdc_address, abi=abi_erc20)

# Checking USDC balance
usdc_decimals = usdc.functions.decimals().call()
usdc_balance = usdc.functions.balanceOf(wallet_address).call()
readable_usdc_balance = usdc_balance / 10 ** usdc_decimals
print(f"USDC Balance: { readable_usdc_balance }")
assert readable_usdc_balance > 0, "Not enough USDC tokens to swap."

# Asking for user's input on amount to swap
readable_swap_amount = float(input("Amount to Swap: "))

# Converting readable_amount into uint256 format
amount_to_swap = int(readable_swap_amount * 10 ** usdc_decimals)
print(f"Amount to swap was { amount_to_swap }")