#!/usr/bin/env python3
"""
integration_agent.py - Connects existing websites/companies to your DAO system
Reuses your existing AI agent infrastructure and smart contracts
"""

import os
import json
import logging
import requests
from web3 import Web3
from dotenv import load_dotenv

# Import your existing agents
from autonomous.ai_builder_agent import MarketplaceAgent
from autonomous.complete_oracle import CompleteOracle
from zialiel.governance.wisdom_oracle import RecursiveWisdomOracle

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationAgent")

class IntegrationAgent(MarketplaceAgent):
    """
    Integrates existing websites/companies with your DAO ecosystem.
    Inherits from your working MarketplaceAgent so it can already:
    - Connect to blockchain
    - Submit jobs
    - Earn reputation
    """
    
    def __init__(self):
        # Initialize the base MarketplaceAgent first
        super().__init__()
        
        # Contract addresses
        self.entity_stack_address = os.getenv("ENTITY_STACK_ADDRESS")
        self.dao_template_address = os.getenv("DAO_TEMPLATE_ADDRESS")
        
        # Load EntityStack contract
        if self.entity_stack_address:
            with open("contracts/EntityStack.json") as f:
                entity_abi = json.load(f).get("abi")
            self.entity_stack = self.w3.eth.contract(
                address=self.entity_stack_address,
                abi=entity_abi
            )
        
        # Connectors for external platforms
        self.connectors = {}
        
        # Wisdom Oracle for ethical validation
        self.wisdom_oracle = RecursiveWisdomOracle(
            api_key=os.getenv("XAI_API_KEY"),
            model=os.getenv("ORACLE_MODEL", "grok-4")
        )
        
        logger.info("✅ Integration Agent initialized")
        logger.info(f"   - Can connect to: WordPress, Shopify, QuickBooks, Stripe")
        logger.info(f"   - Can create legal entities via EntityStack.sol")
        logger.info(f"   - Uses Wisdom Oracle for ethical checks")
    
    # ============================================================
    # CONNECTOR REGISTRATION
    # ============================================================
    
    def register_wordpress(self, site_url, username, password):
        """Connect to a WordPress site"""
        self.connectors['wordpress'] = WordPressConnector(site_url, username, password)
        logger.info(f"📝 Connected to WordPress: {site_url}")
        return True
    
    def register_shopify(self, shop_url, api_key, password):
        """Connect to a Shopify store"""
        self.connectors['shopify'] = ShopifyConnector(shop_url, api_key, password)
        logger.info(f"🛍️ Connected to Shopify: {shop_url}")
        return True
    
    def register_quickbooks(self, client_id, client_secret, refresh_token):
        """Connect to QuickBooks accounting"""
        self.connectors['quickbooks'] = QuickBooksConnector(client_id, client_secret, refresh_token)
        logger.info(f"📊 Connected to QuickBooks")
        return True
    
    def register_stripe(self, api_key):
        """Connect to Stripe payments"""
        self.connectors['stripe'] = StripeConnector(api_key)
        logger.info(f"💳 Connected to Stripe")
        return True
    
    # ============================================================
    # SYNC FUNCTIONS
    # ============================================================
    
    def sync_wordpress_to_dao(self, dao_did):
        """Sync WordPress content to DAO as proposals"""
        if 'wordpress' not in self.connectors:
            logger.error("WordPress not connected")
            return False
        
        wp = self.connectors['wordpress']
        
        # Get recent posts
        posts = wp.get_recent_posts(limit=10)
        
        for post in posts:
            # Create a proposal for each post
            proposal = {
                "title": f"Content Review: {post['title']}",
                "description": post['excerpt'],
                "content_hash": self._store_on_ipfs(post['content']),
                "author_did": self._map_user_to_did(post['author_email']),
                "timestamp": post['date']
            }
            
            # Check with Wisdom Oracle
            verdict = self.wisdom_oracle.analyze_question(
                f"Should this content be approved? {post['title']}: {post['excerpt']}"
            )
            
            if "approve" in verdict.lower():
                # Submit to DAO
                self._submit_proposal(dao_did, proposal)
                logger.info(f"📄 Submitted post: {post['title']}")
        
        return True
    
    def sync_shopify_to_dao(self, dao_did):
        """Sync Shopify products and orders to DAO treasury"""
        if 'shopify' not in self.connectors:
            logger.error("Shopify not connected")
            return False
        
        shopify = self.connectors['shopify']
        
        # Get recent orders
        orders = shopify.get_recent_orders(limit=20)
        
        total_revenue = 0
        for order in orders:
            total_revenue += float(order['total_price'])
        
        # Create treasury report
        report = {
            "dao_did": dao_did,
            "period": "last_30_days",
            "revenue": total_revenue,
            "order_count": len(orders),
            "products_sold": sum(len(o['line_items']) for o in orders)
        }
        
        # Store report on IPFS
        report_hash = self._store_on_ipfs(json.dumps(report))
        
        # Update DAO treasury via smart contract
        if self.entity_stack:
            txn = self.entity_stack.functions.updateTreasury(
                dao_did,
                report_hash,
                int(total_revenue * 100)  # Convert to cents/wei
            ).build_transaction({
                'from': self.agent_address,
                'nonce': self.w3.eth.get_transaction_count(self.agent_address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
            self.w3.eth.send_raw_transaction(signed.rawTransaction)
            logger.info(f"💰 Updated treasury with {total_revenue} revenue")
        
        return True
    
    def _store_on_ipfs(self, content):
        """Store content on IPFS using inherited method"""
        return self.ipfs.add_str(content)
    
    def _map_user_to_did(self, email):
        """Map external user email to Zialiel DID"""
        # Simple mapping – in production, use DID registry
        return f"did:zialiel:user:{hash(email)}"
    
    def _submit_proposal(self, dao_did, proposal):
        """Submit proposal to DAO governance"""
        # This would call your DAO governance contract
        logger.info(f"📝 Proposal submitted to {dao_did}: {proposal['title']}")
        return True
    
    # ============================================================
    # LEGAL ENTITY INTEGRATION (EntityStack.sol)
    # ============================================================
    
    def register_company(self, company_name, jurisdiction, operating_agreement_ipfs):
        """Register a traditional company as a legal entity on-chain"""
        if not self.entity_stack:
            logger.error("EntityStack contract not loaded")
            return False
        
        # Check with Wisdom Oracle first
        verdict = self.wisdom_oracle.ask(
            f"Should we integrate {company_name} as a {jurisdiction} entity?"
        )
        
        if "not align" in verdict.lower():
            logger.warning(f"Wisdom Oracle advises against integrating {company_name}")
            return False
        
        # Create DID for the company
        company_did = f"did:zialiel:company:{hash(company_name)}"
        
        # Register on EntityStack
        txn = self.entity_stack.functions.registerEntity(
            company_did,
            company_name,
            jurisdiction,
            operating_agreement_ipfs
        ).build_transaction({
            'from': self.agent_address,
            'nonce': self.w3.eth.get_transaction_count(self.agent_address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            logger.info(f"✅ Company {company_name} registered as {company_did}")
            return company_did
        else:
            logger.error("❌ Registration failed")
            return False
    
    def link_company_to_dao(self, company_did, dao_address):
        """Link a registered company to an existing DAO"""
        if not self.entity_stack:
            return False
        
        txn = self.entity_stack.functions.linkToDAO(
            company_did,
            dao_address
        ).build_transaction({
            'from': self.agent_address,
            'nonce': self.w3.eth.get_transaction_count(self.agent_address),
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
        self.w3.eth.send_raw_transaction(signed.rawTransaction)
        logger.info(f"🔗 Company {company_did} linked to DAO {dao_address}")
        return True
    
    # ============================================================
    # MAIN INTEGRATION FLOW
    # ============================================================
    
    def integrate_business(self, business_data):
        """
        Complete integration flow for a business:
        1. Connect external platforms
        2. Create DAO
        3. Register legal entity
        4. Link everything
        """
        logger.info(f"🚀 Starting integration for {business_data['name']}")
        
        # Step 1: Connect platforms
        if 'wordpress' in business_data:
            self.register_wordpress(**business_data['wordpress'])
        
        if 'shopify' in business_data:
            self.register_shopify(**business_data['shopify'])
        
        # Step 2: Create DAO (using your future DAOTemplate.sol)
        dao_address = self._create_dao(business_data['name'], business_data['members'])
        
        # Step 3: Register legal entity
        company_did = self.register_company(
            business_data['name'],
            business_data['jurisdiction'],
            business_data['operating_agreement']
        )
        
        # Step 4: Link company to DAO
        if company_did and dao_address:
            self.link_company_to_dao(company_did, dao_address)
        
        # Step 5: Sync initial data
        if 'wordpress' in business_data:
            self.sync_wordpress_to_dao(company_did)
        
        if 'shopify' in business_data:
            self.sync_shopify_to_dao(company_did)
        
        logger.info(f"✅ Integration complete for {business_data['name']}")
        return {
            "dao_address": dao_address,
            "company_did": company_did,
            "status": "integrated"
        }
    
    def _create_dao(self, name, members):
        """Create a new DAO (placeholder – will use your DAOTemplate.sol)"""
        logger.info(f"🏛️ Creating DAO: {name}")
        # This will call your DAOTemplate.sol when deployed
        return f"0x{hash(name)}"  # Placeholder


# ============================================================
# PLATFORM CONNECTORS
# ============================================================

class WordPressConnector:
    def __init__(self, site_url, username, password):
        self.site_url = site_url.rstrip('/')
        self.auth = (username, password)
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
    
    def get_recent_posts(self, limit=10):
        """Get recent WordPress posts"""
        try:
            response = requests.get(
                f"{self.api_base}/posts",
                params={"per_page": limit, "status": "publish"},
                auth=self.auth
            )
            response.raise_for_status()
            
            posts = []
            for post in response.json():
                # Get author email
                author_response = requests.get(
                    f"{self.api_base}/users/{post['author']}",
                    auth=self.auth
                )
                author = author_response.json() if author_response.ok else {"email": "unknown"}
                
                posts.append({
                    "id": post['id'],
                    "title": post['title']['rendered'],
                    "excerpt": post['excerpt']['rendered'],
                    "content": post['content']['rendered'],
                    "date": post['date'],
                    "author_email": author.get('email', 'unknown')
                })
            return posts
        except Exception as e:
            logger.error(f"WordPress API error: {e}")
            return []

class ShopifyConnector:
    def __init__(self, shop_url, api_key, password):
        self.shop_url = shop_url.rstrip('/')
        self.auth = (api_key, password)
    
    def get_recent_orders(self, limit=20):
        """Get recent Shopify orders"""
        try:
            response = requests.get(
                f"https://{self.shop_url}/admin/api/2024-01/orders.json",
                params={"status": "any", "limit": limit},
                auth=self.auth
            )
            response.raise_for_status()
            
            orders = []
            for order in response.json().get('orders', []):
                orders.append({
                    "id": order['id'],
                    "total_price": order['total_price'],
                    "currency": order['currency'],
                    "created_at": order['created_at'],
                    "line_items": order['line_items']
                })
            return orders
        except Exception as e:
            logger.error(f"Shopify API error: {e}")
            return []

class QuickBooksConnector:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self._refresh_access_token()
    
    def _refresh_access_token(self):
        # OAuth2 token refresh logic here
        pass

class StripeConnector:
    def __init__(self, api_key):
        self.api_key = api_key
        import stripe
        stripe.api_key = api_key
        self.stripe = stripe
    
    def get_recent_transactions(self, limit=20):
        """Get recent Stripe transactions"""
        try:
            charges = self.stripe.Charge.list(limit=limit)
            return [{
                "id": c.id,
                "amount": c.amount / 100,  # Convert cents to dollars
                "currency": c.currency,
                "created": c.created,
                "customer": c.customer,
                "description": c.description
            } for c in charges.data]
        except Exception as e:
            logger.error(f"Stripe error: {e}")
            return []


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    agent = IntegrationAgent()
    
    print("\n" + "★" * 60)
    print("🤝 INTEGRATION AGENT".center(58))
    print("★" * 60)
    print("\nThis agent connects existing websites/companies to your DAO system.")
    print("\nOptions:")
    print("1. Integrate a business (full flow)")
    print("2. Connect WordPress site")
    print("3. Connect Shopify store")
    print("4. Register a company as legal entity")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "1":
        business = {
            "name": input("Business name: "),
            "jurisdiction": input("Jurisdiction (e.g., 'Norway', 'Wyoming LLC'): "),
            "operating_agreement": input("Operating agreement IPFS hash (or press Enter for none): ") or "QmPlaceholder",
            "wordpress": {
                "site_url": input("WordPress URL (or press Enter to skip): "),
                "username": input("WordPress username: ") if input("WordPress URL? ") else "",
                "password": input("WordPress password: ") if input("WordPress URL? ") else ""
            } if input("Connect WordPress? (y/n): ").lower() == 'y' else None,
            "shopify": {
                "shop_url": input("Shopify shop URL: "),
                "api_key": input("Shopify API key: "),
                "password": input("Shopify password: ")
            } if input("Connect Shopify? (y/n): ").lower() == 'y' else None
        }
        agent.integrate_business(business)
