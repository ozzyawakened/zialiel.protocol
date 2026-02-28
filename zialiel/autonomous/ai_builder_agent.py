# ai_builder_agent.py
import openai
from web3 import Web3
import json

# Connect to your blockchain
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
contract = w3.eth.contract(address="0x...", abi=json.loads("..."))

# Listen for events
def handle_request(event):
    request_id = event['args']['id']
    description = event['args']['description']
    
    # Generate website code using AI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system", 
            "content": "You are a website builder. Generate complete HTML/CSS/JS based on descriptions."
        }, {
            "role": "user",
            "content": description
        }]
    )
    
    code = response.choices[0].message.content
    
    # Store on IPFS
    import ipfshttpclient
    client = ipfshttpclient.connect()
    ipfs_hash = client.add_str(code)
    
    # Call smart contract to fulfill
    contract.functions.fulfillRequest(request_id, ipfs_hash).transact()

# Listen forever
event_filter = contract.events.RequestCreated.create_filter()
while True:
    for event in event_filter.get_new_entries():
        handle_request(event)
    time.sleep(5)
