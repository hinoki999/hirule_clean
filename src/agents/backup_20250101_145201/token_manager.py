from typing import Dict, Optional
import logging
from web3 import Web3
from eth_typing import Address
from src.agents.base import BaseAgent
from src.agents.capability import Capability

class TokenManagerError(Exception):
    pass

NLT_ABI = [
    {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","type":"address"},{"internalType":"uint256","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","type":"bool"}],"stateMutability":"nonpayable","type":"function"}
]

class TokenManager(BaseAgent):
    def __init__(self, config: Dict):
        super().__init__(config)
        self._validate_config(config)
        self.contract_address = config["contract_address"]
        self.wallet_address = config["wallet_address"]
        self.logger = logging.getLogger(__name__)
        
        # Initialize Web3 and contract
        try:
            provider = Web3.HTTPProvider(config["eth_rpc_url"])
            self.w3 = Web3(provider)
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=NLT_ABI
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Web3: {str(e)}")
            raise TokenManagerError(f"Failed to initialize Web3: {str(e)}")

    def _validate_config(self, config: Dict) -> None:
        required_fields = ["eth_rpc_url", "contract_address", "wallet_address"]
        if not all(field in config for field in required_fields):
            raise TokenManagerError("Missing required configuration fields")

    async def setup(self):
        try:
            await self.message_bus.subscribe("token_operation", self._handle_token_operation)
            await self._verify_contract()
        except Exception as e:
            raise TokenManagerError(f"Setup failed: {str(e)}")

    async def _verify_contract(self):
        try:
            total_supply = self.contract.functions.totalSupply().call()
            self.logger.info(f"Connected to NLT token contract. Total supply: {total_supply}")
        except Exception as e:
            raise TokenManagerError(f"Contract verification failed: {str(e)}")

    async def _handle_token_operation(self, message: Dict):
        try:
            operation = message.get("operation")
            if operation == "transfer":
                await self._handle_transfer(message)
            elif operation == "balance":
                await self._handle_balance_check(message)
            else:
                raise TokenManagerError(f"Unknown operation: {operation}")
        except Exception as e:
            self.logger.error(f"Error handling token operation: {str(e)}")
            raise

    async def _handle_balance_check(self, message: Dict):
        try:
            address = message.get("address", self.wallet_address)
            balance = self.contract.functions.balanceOf(
                Web3.to_checksum_address(address)
            ).call()
            
            await self.message_bus.publish("token_operation_result", {
                "operation": "balance",
                "address": address,
                "balance": balance
            })
        except Exception as e:
            self.logger.error(f"Balance check failed: {str(e)}")
            raise TokenManagerError(f"Balance check failed: {str(e)}")

    async def _handle_transfer(self, message: Dict):
        try:
            to_address = message["to_address"]
            amount = message["amount"]
            
            tx = self.contract.functions.transfer(
                Web3.to_checksum_address(to_address),
                amount
            ).build_transaction({
                'from': Web3.to_checksum_address(self.wallet_address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            })
            
            # Note: In production, add key management and transaction signing here
            
            await self.message_bus.publish("token_operation_result", {
                "operation": "transfer",
                "status": "ready",
                "tx": tx,
                "to_address": to_address,
                "amount": amount
            })
            
        except Exception as e:
            self.logger.error(f"Transfer failed: {str(e)}")
            raise TokenManagerError(f"Transfer failed: {str(e)}")
