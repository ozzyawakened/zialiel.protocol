# autonomous_builder.py
from wisdom_oracle import WisdomOracle
import openai
import ipfshttpclient
from web3 import Web3
import json
import time

class AutonomousBuilder:
    def __init__(self, contract_address, abi):
        self.wisdom = WisdomOracle()
        self.w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
        self.contract = self.w3.eth.contract(
            address=contract_address, 
            abi=abi
        )
        self.ipfs = ipfshttpclient.connect()
        
    def check_alignment(self, request):
        """Ensure request aligns with wisdom"""
        result = self.wisdom.analyze_proposal(
            "Creation Request",
            request,
            ["creativity", "justice", "stewardship"],
            False
        )
        return result.passes, result.confidence
    
    def generate_creation(self, request):
        """Generate code based on request"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a creator. Generate complete, working code based on requests. Include HTML, CSS, JavaScript, or smart contracts as needed."
            }, {
                "role": "user",
                "content": request
            }]
        )
        return response.choices[0].message.content
    
    def store_on_ipfs(self, content):
        """Store creation permanently"""
        hash = self.ipfs.add_str(content)
        return hash
    
    def fulfill_request(self, request_id, ipfs_hash):
        """Call smart contract to complete"""
        self.contract.functions.fulfillRequest(
            request_id, 
            ipfs_hash
        ).transact()
    
    def listen_and_create(self):
        """Main loop"""
        event_filter = self.contract.events.RequestCreated.create_filter()
        
        while True:
            for event in event_filter.get_new_entries():
                request_id = event['args']['id']
                description = event['args']['description']
                
                print(f"📨 New request #{request_id}: {description}")
                
                # Check alignment
                aligned, confidence = self.check_alignment(description)
                if not aligned:
                    print(f"⚠️ Request rejected by wisdom (confidence: {confidence:.0%})")
                    continue
                
                print(f"✅ Wisdom aligned ({confidence:.0%})")
                
                # Generate
                print("⚙️ Generating...")
                code = self.generate_creation(description)
                
                # Store
                print("💾 Storing on IPFS...")
                ipfs_hash = self.store_on_ipfs(code)
                
                # Fulfill
                print(f"✅ Complete! IPFS: {ipfs_hash}")
                self.fulfill_request(request_id, ipfs_hash)
                
                print(f"🌐 View at: https://ipfs.io/ipfs/{ipfs_hash}")
            
            time.sleep(5)

# Run it
builder = AutonomousBuilder("0x...", "...")
builder.listen_and_create()
