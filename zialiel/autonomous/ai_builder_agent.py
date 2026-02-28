#!/usr/bin/env python3
# ai_builder_agent.py – Grok version with Wisdom Oracle and error handling

import openai
from web3 import Web3
import ipfshttpclient
import json
import time
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------------------------------------------
# CONFIGURATION (from environment variables)
# -------------------------------------------------------------------
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
CONTRACT_ABI_PATH = os.getenv("CONTRACT_ABI_PATH", "./WebsiteBuilder.json")
PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
AGENT_ADDRESS = os.getenv("AGENT_ADDRESS")
RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
IPFS_URL = os.getenv("IPFS_URL", "/ip4/127.0.0.1/tcp/5001/http")

# Grok-specific environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1/")
XAI_MODEL = os.getenv("XAI_MODEL", "grok-4")  # or grok-3, grok-3-mini

# -------------------------------------------------------------------
# SETUP LOGGING
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Grok-Builder")

# -------------------------------------------------------------------
# CONFIGURE GROK (xAI) – THIS IS THE MAIN CHANGE!
# -------------------------------------------------------------------
def configure_grok():
    """Configure the OpenAI library to use xAI/Grok"""
    if not XAI_API_KEY:
        logger.error("XAI_API_KEY missing in .env file")
        sys.exit(1)
    
    openai.api_key = XAI_API_KEY
    openai.base_url = XAI_BASE_URL  # <-- This is the trick!
    logger.info(f"Grok configured with base URL: {XAI_BASE_URL}, model: {XAI_MODEL}")

# -------------------------------------------------------------------
# LOAD CONTRACT ABI
# -------------------------------------------------------------------
def load_contract_abi():
    try:
        with open(CONTRACT_ABI_PATH) as f:
            contract_json = json.load(f)
            # If file is from Truffle/Hardhat, ABI might be in "abi" field
            if "abi" in contract_json:
                return contract_json["abi"]
            return contract_json
    except FileNotFoundError:
        logger.error(f"ABI file not found: {CONTRACT_ABI_PATH}")
        sys.exit(1)

# -------------------------------------------------------------------
# CONNECT TO BLOCKCHAIN
# -------------------------------------------------------------------
def connect_to_blockchain():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        logger.error(f"Could not connect to blockchain at {RPC_URL}")
        sys.exit(1)
    
    abi = load_contract_abi()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    logger.info(f"Connected to contract {CONTRACT_ADDRESS}")
    
    return w3, contract

# -------------------------------------------------------------------
# WISDOM ORACLE – CHECK THAT CODE IS ETHICAL
# -------------------------------------------------------------------
def validate_with_wisdom_oracle(description, code):
    """
    Use the Wisdom Oracle (from your system) to validate that generated code
    contains no harmful elements and is ethically sound.
    """
    # Here you can connect to your actual Wisdom Oracle
    # from wisdom_oracle import WisdomOracle
    # oracle = WisdomOracle()
    # verdict = oracle.analyze_proposal(...)
    # return verdict.passes, verdict.reasoning
    
    # Simple security check (temporary)
    forbidden_patterns = [
        "<script>alert(",  # XSS
        "eval(",           # Dangerous JavaScript
        "document.cookie", # Cookie theft
        "malware",
        "phishing"
    ]
    
    code_lower = code.lower()
    for pattern in forbidden_patterns:
        if pattern in code_lower:
            logger.warning(f"ORACLE: Rejected code with pattern: {pattern}")
            return False, f"Contains forbidden pattern: {pattern}"
    
    # Check code length (sanity check)
    if len(code) < 100:
        logger.warning("ORACLE: Code suspiciously short")
        return False, "Generated code is too short"
    
    return True, "Approved"

# -------------------------------------------------------------------
# GENERATE WEBSITE WITH GROK
# -------------------------------------------------------------------
def generate_website(description):
    try:
        logger.info(f"Generating website with {XAI_MODEL}...")
        
        response = openai.ChatCompletion.create(
            model=XAI_MODEL,  # Uses Grok model from .env
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional website builder. "
                        "Generate complete, self-contained HTML/CSS/JavaScript code "
                        "based on the user's description. Include styling and make it responsive. "
                        "Return ONLY the code, no explanations, no markdown formatting."
                    )
                },
                {"role": "user", "content": description}
            ],
            temperature=0.7,
            max_tokens=4000  # Grok 4 has 256K context, so we can be generous
        )
        
        code = response.choices[0].message.content
        
        # Remove any markdown code blocks (```html ```)
        if code.startswith("```"):
            # Split by ``` and take the middle part
            parts = code.split("```")
            if len(parts) >= 2:
                code = parts[1]
                # Remove language identifier if present
                if code.startswith("html"):
                    code = code[4:]
                elif code.startswith("javascript"):
                    code = code[10:]
                elif code.startswith("css"):
                    code = code[3:]
        
        # Trim whitespace
        code = code.strip()
        
        logger.info(f"Website generated, {len(code)} characters")
        return code
        
    except Exception as e:
        logger.error(f"Grok error: {e}")
        return None

# -------------------------------------------------------------------
# STORE ON IPFS
# -------------------------------------------------------------------
def store_on_ipfs(code, request_id):
    try:
        client = ipfshttpclient.connect(IPFS_URL)
        
        # Store with metadata
        content = {
            "code": code,
            "generated_at": time.time(),
            "request_id": request_id,
            "model": XAI_MODEL,
            "agent": "Grok-Builder"
        }
        
        # Convert to JSON string and add to IPFS
        json_str = json.dumps(content)
        ipfs_hash = client.add_str(json_str)
        
        logger.info(f"Stored on IPFS: {ipfs_hash}")
        return ipfs_hash
        
    except Exception as e:
        logger.error(f"IPFS error: {e}")
        return None

# -------------------------------------------------------------------
# FULFILL REQUEST ON BLOCKCHAIN
# -------------------------------------------------------------------
def fulfill_request(w3, contract, request_id, ipfs_hash):
    try:
        # Get current nonce
        nonce = w3.eth.get_transaction_count(AGENT_ADDRESS)
        
        # Build transaction
        txn = contract.functions.fulfillRequest(
            request_id, 
            ipfs_hash
        ).build_transaction({
            'from': AGENT_ADDRESS,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign
        signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        
        # Send
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for receipt
        logger.info(f"Waiting for transaction {txn_hash.hex()}...")
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
        
        if receipt.status == 1:
            logger.info(f"Request {request_id} fulfilled! Tx: {txn_hash.hex()}")
            return True
        else:
            logger.error(f"Transaction failed: {txn_hash.hex()}")
            return False
            
    except Exception as e:
        logger.error(f"Blockchain error: {e}")
        return False

# -------------------------------------------------------------------
# MAIN LOOP – LISTEN FOR EVENTS
# -------------------------------------------------------------------
def main():
    # Check that all required environment variables exist
    required_vars = {
        "PRIVATE_KEY": PRIVATE_KEY,
        "AGENT_ADDRESS": AGENT_ADDRESS,
        "XAI_API_KEY": XAI_API_KEY,
        "CONTRACT_ADDRESS": CONTRACT_ADDRESS
    }
    
    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.info("Create a .env file with the following:")
        logger.info("""
XAI_API_KEY=your-key-here
AGENT_PRIVATE_KEY=your-private-key-here
AGENT_ADDRESS=your-address-here
CONTRACT_ADDRESS=0x...
CONTRACT_ABI_PATH=./WebsiteBuilder.json
RPC_URL=http://localhost:8545
IPFS_URL=/ip4/127.0.0.1/tcp/5001/http
XAI_MODEL=grok-4
        """)
        sys.exit(1)
    
    # Configure Grok
    configure_grok()
    
    # Connect to blockchain
    w3, contract = connect_to_blockchain()
    
    # Check that agent is authorized in the contract
    try:
        is_authorized = contract.functions.authorizedAgents(AGENT_ADDRESS).call()
        if not is_authorized:
            logger.warning(f"Agent {AGENT_ADDRESS} is not authorized in contract!")
            logger.info("Call authorizeAgent() from contract owner first")
            # Continue anyway? Or exit? Let's warn but continue
    except Exception as e:
        logger.error(f"Could not check authorization: {e}")
    
    # Create event filter
    event_filter = contract.events.RequestCreated.create_filter(fromBlock='latest')
    logger.info("Starting event listener. Press Ctrl+C to stop.")
    
    # Statistics
    stats = {
        "requests_processed": 0,
        "successful": 0,
        "failed": 0
    }
    
    try:
        while True:
            # Get new events
            for event in event_filter.get_new_entries():
                request_id = event['args']['id']
                description = event['args']['description']
                requester = event['args']['requester']
                
                stats["requests_processed"] += 1
                logger.info(f"New request #{request_id}: {description[:50]}... from {requester}")
                
                # 1. Generate website
                code = generate_website(description)
                if not code:
                    logger.error(f"Could not generate code for #{request_id}")
                    stats["failed"] += 1
                    continue
                
                # 2. Validate with Wisdom Oracle
                valid, message = validate_with_wisdom_oracle(description, code)
                if not valid:
                    logger.warning(f"Oracle rejected #{request_id}: {message}")
                    # Here you could send a "rejected" event on-chain
                    stats["failed"] += 1
                    continue
                
                # 3. Store on IPFS
                ipfs_hash = store_on_ipfs(code, request_id)
                if not ipfs_hash:
                    stats["failed"] += 1
                    continue
                
                # 4. Fulfill on blockchain
                success = fulfill_request(w3, contract, request_id, ipfs_hash)
                if success:
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1
                
                # Log stats every 10 requests
                if stats["requests_processed"] % 10 == 0:
                    logger.info(f"STATS: Processed: {stats['requests_processed']}, "
                               f"Successful: {stats['successful']}, Failed: {stats['failed']}")
            
            # Wait before next check
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
        logger.info(f"Final stats: Processed: {stats['requests_processed']}, "
                   f"Successful: {stats['successful']}, Failed: {stats['failed']}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
