import os
import time
from web3 import Web3

RPC = os.environ.get("RPC_URL")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "10"))

if not RPC:
    raise SystemExit("Error: set RPC_URL environment variable (e.g. https://mainnet.infura.io/v3/YOUR_KEY)")

w3 = Web3(Web3.HTTPProvider(RPC))

def format_eth(wei):
    try:
        return w3.fromWei(wei, "ether")
    except Exception:
        return wei

def get_balance(addr):
    return w3.eth.get_balance(addr)

def scan_blocks_for_address(address, last_block):
    current = w3.eth.block_number
    for b in range(last_block + 1, current + 1):
        block = w3.eth.get_block(b, full_transactions=True)
        for tx in block.transactions:
            tx_to = tx.to.lower() if tx.to else None
            tx_from = tx['from'].lower()
            if tx_to == address.lower() or tx_from == address.lower():
                value_eth = format_eth(tx.value)
                print(f"[block {b}] tx {tx.hash.hex()} from {tx_from} to {tx_to} value {value_eth} ETH")
    return current

def run_bot():
    print("Web3 Job Bot Running...")
    address = None
    last_block = w3.eth.block_number
    last_balance = None

    while True:
        addr_now = os.environ.get("ADDRESS")
        if addr_now:
            try:
                address = Web3.toChecksumAddress(addr_now)
            except Exception:
                print("ADDRESS env var is invalid checksum address; please set a valid 0x... address.")
                address = None

        if address:
            print(f"Monitoring address: {address}")
            try:
                bal = get_balance(address)
                if last_balance is None or bal != last_balance:
                    print(f"Balance for {address}: {format_eth(bal)} ETH")
                    last_balance = bal
            except Exception as e:
                print("Error getting balance:", e)

            try:
                last_block = scan_blocks_for_address(address, last_block)
            except Exception as e:
                print("Error scanning blocks:", e)
        else:
            print("ADDRESS not set. Export ADDRESS env var to monitor an address (e.g. export ADDRESS=0x..).")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_bot()
