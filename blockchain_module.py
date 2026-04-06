import hashlib
import json
import time
import os

LEDGER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blockchain_ledger.json')

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
        
    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_ledger()
        
    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        self.chain.append(genesis_block)
        self.save_ledger()

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        self.save_ledger()
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def save_ledger(self):
        with open(LEDGER_FILE, 'w') as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def load_ledger(self):
        if os.path.exists(LEDGER_FILE):
            try:
                with open(LEDGER_FILE, 'r') as f:
                    data = json.load(f)
                    self.chain = []
                    for b in data:
                        block = Block(b['index'], b['timestamp'], b['data'], b['previous_hash'])
                        block.hash = b['hash']
                        self.chain.append(block)
            except Exception:
                self.chain = []
                self.create_genesis_block()
        else:
            self.create_genesis_block()
            
    def get_chain(self):
        return [block.to_dict() for block in self.chain]

    def verify_transaction(self, tx_hash):
        for block in self.chain:
            if isinstance(block.data, dict) and block.data.get('transaction_hash') == tx_hash:
                return True
        return False

# Global instance
ledger = Blockchain()
