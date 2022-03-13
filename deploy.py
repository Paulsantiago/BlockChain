from audioop import add
import json
from queue import SimpleQueue
from web3 import Web3

# from web3 import Web3

# In the video, we forget to `install_solc`
# from solcx import compile_standard
# import solcx
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

import os

load_dotenv()


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# We add these two lines that we forgot from the video!
print("Installing...")
install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)
with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)
# print(compiled_sol)
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


#w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/a0d6601d9af6487b82a098ce37a868b0"))
# chainlink
chain_id = 4
my_address = "0xfceC616C768350E8A3CC5456566Bd0c1dFe39415"
# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# signed_txn = w3.eth.account.
# print(transaction)
private_key = os.getenv("PRIVATE_KEY")
print(private_key)
signed_thx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# sed transaction
# tx_hash = w3.eth.send_raw_transaction(signed_thx.rawTransaction)
tx_hash = w3.eth.send_raw_transaction(signed_thx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
nonce = w3.eth.getTransactionCount(my_address)
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(30).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
print("new nonce :" , nonce)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_txn)
print(simple_storage.functions.retrieve().call())
