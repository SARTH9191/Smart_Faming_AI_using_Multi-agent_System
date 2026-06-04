"""
⛓️ BLOCKCHAIN AGENT
Mini blockchain for Green Token rewards and farm action logging
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List
import os

class Block:
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class BlockchainAgent:
    def __init__(self, ledger_path: str = "../blockchain/ledger.json"):
        self.name = "Blockchain Agent"
        self.ledger_path = ledger_path
        self.chain = []
        self.token_balances = {}
        self.load_blockchain()
    
    def load_blockchain(self):
        """Load blockchain from file or create genesis block"""
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        
        try:
            with open(self.ledger_path, 'r') as f:
                data = json.load(f)
                self.chain = data.get("chain", [])
                self.token_balances = data.get("balances", {})
        except (FileNotFoundError, json.JSONDecodeError):
            # Create genesis block
            self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            data={"message": "Genesis Block - Smart Farming Blockchain"},
            previous_hash="0"
        )
        self.chain.append(genesis_block.to_dict())
        self.save_blockchain()
    
    def add_transaction(self, farm_id: str, action_type: str, 
                       action_details: str, green_tokens: int) -> Dict[str, Any]:
        """Add a new transaction to the blockchain"""
        
        previous_block = self.chain[-1] if self.chain else None
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            data={
                "farm_id": farm_id,
                "action_type": action_type,
                "action_details": action_details,
                "green_tokens_earned": green_tokens,
                "transaction_type": "farm_action"
            },
            previous_hash=previous_block["hash"] if previous_block else "0"
        )
        
        # Validate block
        if self.validate_block(new_block, previous_block):
            self.chain.append(new_block.to_dict())
            
            # Update token balance
            if farm_id not in self.token_balances:
                self.token_balances[farm_id] = 0
            self.token_balances[farm_id] += green_tokens
            
            # Save to file
            self.save_blockchain()
            
            return {
                "status": "success",
                "block_index": new_block.index,
                "hash": new_block.hash,
                "tokens_earned": green_tokens,
                "new_balance": self.token_balances[farm_id]
            }
        else:
            return {"status": "error", "message": "Block validation failed"}
    
    def validate_block(self, block: Block, previous_block: Dict = None) -> bool:
        """Validate a block"""
        if previous_block:
            if block.previous_hash != previous_block["hash"]:
                return False
        return True
    
    def calculate_green_tokens(self, action_type: str, action_details: Dict = None) -> int:
        """Calculate Green Tokens earned for an action"""
        
        token_rewards = {
            "smart_irrigation": 10,
            "organic_fertilizer": 15,
            "drip_irrigation": 20,
            "crop_rotation": 12,
            "rainwater_harvesting": 25,
            "solar_pump": 30,
            "composting": 15,
            "zero_tillage": 18,
            "mulching": 10,
            "integrated_pest_management": 20
        }
        
        return token_rewards.get(action_type, 5)
    
    def get_balance(self, farm_id: str) -> int:
        """Get Green Token balance for a farm"""
        return self.token_balances.get(farm_id, 0)
    
    def get_recent_logs(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent blockchain transactions"""
        
        recent_blocks = self.chain[-limit:] if len(self.chain) > limit else self.chain
        
        return {
            "agent": self.name,
            "total_blocks": len(self.chain),
            "recent_transactions": recent_blocks,
            "chain_valid": self.validate_chain()
        }
    
    def validate_chain(self) -> bool:
        """Validate entire blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current["previous_hash"] != previous["hash"]:
                return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        
        total_tokens_issued = sum(self.token_balances.values())
        
        return {
            "agent": self.name,
            "total_blocks": len(self.chain),
            "total_tokens_issued": total_tokens_issued,
            "total_farms": len(self.token_balances),
            "chain_valid": self.validate_chain(),
            "top_performers": self.get_top_performers(5)
        }
    
    def get_top_performers(self, limit: int = 5) -> List[Dict]:
        """Get top farms by Green Token balance"""
        
        sorted_farms = sorted(
            self.token_balances.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"farm_id": farm_id, "green_tokens": tokens}
            for farm_id, tokens in sorted_farms
        ]
    
    def save_blockchain(self):
        """Save blockchain to file"""
        with open(self.ledger_path, 'w') as f:
            json.dump({
                "chain": self.chain,
                "balances": self.token_balances,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def reward_sustainable_action(self, farm_id: str, action_type: str, 
                                  action_details: str) -> Dict[str, Any]:
        """Reward farmer for sustainable action"""
        
        tokens = self.calculate_green_tokens(action_type)
        result = self.add_transaction(farm_id, action_type, action_details, tokens)
        
        return {
            "action": action_type,
            "tokens_earned": tokens,
            "blockchain_result": result,
            "message": f"🌟 Earned {tokens} Green Tokens for {action_type}"
        }
    
    def get_full_chain(self) -> List[Dict]:
        """Get complete blockchain with all blocks"""
        return self.chain
