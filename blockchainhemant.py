import streamlit as st
from web3 import Web3
import json

st.title("🎟️ Bus Ticketing DApp")

# Connect to local Ganache or Infura
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Adjust as needed

# Load ABI
with open('BusTicketingABI.json', 'r') as f:
    abi = json.load(f)

# Contract address
contract_address = '0xYourContractAddressHere'
contract = w3.eth.contract(address=contract_address, abi=abi)

# Wallet setup
private_key = st.text_input("🔑 Enter your private key", type="password")
account = w3.eth.account.from_key(private_key) if private_key else None

if account:
    st.success(f"Connected as {account.address}")

    # Buy Ticket
    if st.button("Buy Ticket"):
        nonce = w3.eth.get_transaction_count(account.address)
        txn = contract.functions.buyTicket().build_transaction({
            'from': account.address,
            'value': contract.functions.ticketPrice().call(),
            'gas': 200000,
            'nonce': nonce
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        st.write("⏳ Buying ticket...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        st.success("✅ Ticket purchased!")

    # View My Tickets
    if st.button("Show My Tickets"):
        ids = contract.functions.getMyTickets().call({'from': account.address})
        for tid in ids:
            t = contract.functions.tickets(tid).call()
            st.markdown(f"**Ticket #{tid}**  \nOwner: `{t[1]}`  \nUsed: `{t[2]}`  \nHash: `{t[3].hex()}`")

    # Use Ticket
    ticket_to_use = st.number_input("Enter Ticket ID to use", min_value=1, step=1)
    if st.button("Use Ticket"):
        nonce = w3.eth.get_transaction_count(account.address)
        txn = contract.functions.useTicket(ticket_to_use).build_transaction({
            'from': account.address,
            'gas': 200000,
            'nonce': nonce
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        st.write("⏳ Using ticket...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        st.success("🎫 Ticket used!")
