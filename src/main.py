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

# Initializing the axlUSDC contract
axlusdc_address = config["AXLUSDC_CONTRACT"]
axlusdc = web3.eth.contract(address=axlusdc_address, abi=abi_erc20)

# Fetching number of decimals for axlUSDC
axlusdc_decimals = axlusdc.functions.decimals().call()

# Checking USDC balance
usdc_decimals = usdc.functions.decimals().call()
usdc_balance = usdc.functions.balanceOf(wallet_address).call()
readable_usdc_balance = usdc_balance / 10 ** usdc_decimals
print(f"USDC Balance: { readable_usdc_balance }")
assert readable_usdc_balance > 0, "Not enough USDC tokens to swap."

# Asking for user's input on amount to swap
# Input can not be zero or less than zero
readable_swap_amount = 0
while readable_swap_amount <= 0:
	try:
		readable_swap_amount = float(input("Amount to Swap: "))
		if readable_swap_amount <= 0:
			raise Exception("Please use numbers greater than 0.")
	except ValueError:
		print("Invalid input, please use numbers greater than 0.")
	except Exception as input_error:
		print(input_error)

# Converting readable_amount into uint256 format
amount_to_swap = int(readable_swap_amount * 10 ** usdc_decimals)

# Running the `get_dy()` function of the pool contract
# To determine how much we would receive for the amount we'll swap
# USDC is at position [1] while axlUSDC is at position [0]
dy = pool.functions.get_dy(1, 0, amount_to_swap).call()
readable_dy = dy / 10 ** axlusdc_decimals
print(f"Swapping { readable_swap_amount } USDC to axlUSDC, we would receive at least { readable_dy } in axlUSDC.")