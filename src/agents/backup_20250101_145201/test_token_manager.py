import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from web3 import Web3
from src.agents.token.token_manager import TokenManager, TokenManagerError

@pytest.fixture
def manager_config():
    return {
        "eth_rpc_url": "https://mainnet.infura.io/v3/your-project-id",
        "contract_address": "0x8bb96795389237bbfb600601b9bbd3924a907207",
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }

@pytest.mark.asyncio
async def test_initialization(manager_config):
    with patch("src.agents.token.token_manager.TokenManager._validate_config"), \
         patch("src.agents.token.token_manager.Web3"):
        manager = TokenManager(manager_config)
        assert manager.contract_address == manager_config["contract_address"]

@pytest.mark.asyncio
async def test_balance_check(manager_config):
    mock_contract = MagicMock()
    mock_contract.functions.balanceOf = MagicMock()
    mock_contract.functions.balanceOf.return_value.call = MagicMock(return_value=1000)
    
    with patch("src.agents.token.token_manager.TokenManager._validate_config"), \
         patch("src.agents.token.token_manager.Web3"):
        manager = TokenManager(manager_config)
        manager.message_bus = AsyncMock()
        manager.contract = mock_contract
        
        test_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        await manager._handle_balance_check({"address": test_address})
        
        mock_contract.functions.balanceOf.assert_called_once()
        manager.message_bus.publish.assert_called_once()
        args = manager.message_bus.publish.call_args[0]
        assert args[0] == "token_operation_result"
        assert args[1]["operation"] == "balance"
        assert args[1]["balance"] == 1000

@pytest.mark.asyncio
async def test_transfer(manager_config):
    mock_contract = MagicMock()
    mock_contract.functions.transfer = MagicMock()
    mock_contract.functions.transfer.return_value.build_transaction = MagicMock(
        return_value={
            "from": manager_config["wallet_address"],
            "gas": 100000,
            "gasPrice": 20000000000,
            "nonce": 1
        }
    )
    
    with patch("src.agents.token.token_manager.TokenManager._validate_config"), \
         patch("src.agents.token.token_manager.Web3") as MockWeb3:
        MockWeb3.to_checksum_address = Web3.to_checksum_address
        
        manager = TokenManager(manager_config)
        manager.message_bus = AsyncMock()
        manager.contract = mock_contract
        manager.w3 = MagicMock()
        manager.w3.eth.gas_price = 20000000000
        manager.w3.eth.get_transaction_count = MagicMock(return_value=1)
        
        test_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        amount = 100
        
        await manager._handle_transfer({
            "to_address": test_address,
            "amount": amount
        })
        
        mock_contract.functions.transfer.assert_called_once_with(
            Web3.to_checksum_address(test_address),
            amount
        )
        manager.message_bus.publish.assert_called_once()
        args = manager.message_bus.publish.call_args[0]
        assert args[0] == "token_operation_result"
        assert args[1]["operation"] == "transfer"
        assert args[1]["status"] == "ready"
        assert args[1]["to_address"] == test_address
        assert args[1]["amount"] == amount
