"""Encountered an error reminder

If we encounter another error: "ImportError: cannot import name 'getargspec' from 'inspect'"
Do this:
	- go to ...lib/python3.11/site-packages/parsimonious/expressions.py
	- change line 9 to import getfullargspec

"""

from settings import config # contains our env variables
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import json
import time

# Initializing the provider and connecting to the chain
provider = HTTPProvider(config["RPC_URL"])
web3 = Web3(provider)
web3.middleware_onion.inject(geth_poa_middleware, layer=0) # needed if not connecting to Ethereum mainnet
assert web3.isConnected(), "Failed to connect to Web3."
print("Connection to Web3 is a success!")

# Vars for wallet address and wallet's private key
wallet_address = config["WALLET_ADDRESS"]
private_key = config["PRIVATE_KEY"]

chain_id = web3.eth.chain_id
nonce = web3.eth.getTransactionCount(wallet_address)

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

# Fetching the index value for the coins to swap
coin_index_zero = pool.functions.coins(0).call()
if coin_index_zero == axlusdc_address:
	axlusdc_coin_index = 0
	usdc_coin_index = 1

# Running the `get_dy()` function of the pool contract
# To determine how much we would receive for the amount we'll swap
# 1st argument is for the coin to send, 2nd is for the coin to receive, lastly is the amount to swap in atomic form
min_amount_to_receive = pool.functions.get_dy(usdc_coin_index, axlusdc_coin_index, amount_to_swap).call()
readable_min_amount_to_receive = min_amount_to_receive / 10 ** axlusdc_decimals
print(f"Swapping { readable_swap_amount } USDC to axlUSDC, we would receive at least { readable_min_amount_to_receive } in axlUSDC.")

# Let the swapping begin!
# Calling the exchange() function and building the transaction
transaction = pool.functions.exchange(usdc_coin_index, axlusdc_coin_index, amount_to_swap, min_amount_to_receive).buildTransaction({ "chainId": chain_id, "from": wallet_address, "nonce": nonce })

# Signing the transaction
signed_transaction = web3.eth.account.sign_transaction(transaction, private_key=private_key)

try:
	# Send the signed transaction
	sent_transaction = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

	# Waiting for transaction receipt
	receipt = web3.eth.wait_for_transaction_receipt(sent_transaction)

	# Looping through the AttributeDict and decoding hex tx hash to string
	for key, value in receipt.items():
		if key == "transactionHash":
			print(f"Swap Transaction Hash: { web3.toHex(value) }")

			# Set a 10s countdown timer before checking the output balance
			def countdown(t):
				print("Counting down...")

				while t:
					mins, secs = divmod(t, 60)
					timer = "{:02d}:{:02d}".format(mins, secs)
					print(timer, end="\r")
					time.sleep(1)
					t -= 1

				print("Done! Now checking for output balance.")

			countdown(10)
except Exception as e:
	print(e)

# Check output token's balance after swapping
axlusdc_balance = axlusdc.functions.balanceOf(wallet_address).call()
readable_axlusdc_balance = axlusdc_balance / 10 ** axlusdc_decimals
print(f"axlUSDC Balance: { readable_axlusdc_balance }")
print("fin.")