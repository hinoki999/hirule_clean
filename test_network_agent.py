<<<<<<< ours
import pytest
import logging
import sys
from src.agents.blockchain.network_agent import NetworkAgent

@pytest.fixture
async def network_agent():
    agent = NetworkAgent(max_peers=3)
    await agent.start()
    yield agent
    await agent.stop()

@pytest.mark.asyncio
async def test_basic_functionality(network_agent):
    # Test peer connection
    peer1 = {
        'peer_id': 'test_peer_1',
        'address': '127.0.0.1',
        'port': 8000
    }
    success = await network_agent.connect_peer({'type': 'connect_peer', **peer1})
    assert success

    # Test broadcasting a transaction
    tx_task = {
        'type': 'broadcast_transaction',
        'transaction': {
            'from': 'wallet1',
            'to': 'wallet2',
            'amount': 1.0
        }
    }
    result = await network_agent.process_task(tx_task)
    assert result['status'] == 'success'

    # Test peer info retrieval
    info_task = {'type': 'get_peer_info'}
    result = await network_agent.process_task(info_task)
    assert len(result['result']['peers']) == 1

@pytest.mark.asyncio
async def test_max_peers(network_agent):
    # Try to connect more peers than max_peers
    for i in range(5):  # More than max_peers (3)
        peer = {
            'peer_id': f'test_peer_{i}',
            'address': '127.0.0.1',
            'port': 8000 + i
        }
        await network_agent.connect_peer({'type': 'connect_peer', **peer})

    # Verify peer count
    info_task = {'type': 'get_peer_info'}
    result = await network_agent.process_task(info_task)
    assert len(result['result']['peers']) == 3  # Should be limited to max_peers

@pytest.mark.asyncio
async def test_network_messages(network_agent):
    # Connect a peer
    peer1 = {
        'peer_id': 'test_peer_1',
        'address': '127.0.0.1',
        'port': 8000
    }
    await network_agent.connect_peer({'type': 'connect_peer', **peer1})

    # Test block broadcasting
    block_task = {
        'type': 'broadcast_block',
        'block': {
            'index': 1,
            'timestamp': '2024-12-20T21:00:00Z',
            'transactions': []
        }
    }
    result = await network_agent.process_task(block_task)
    assert result is not None

    # Test sync request
    sync_task = {
        'type': 'sync_request',
        'peer_id': 'test_peer_1',
        'start_block': 0,
        'end_block': 10
    }
    result = await network_agent.process_task(sync_task)
    assert result is not None

if __name__ == '__main__':
    pytest.main([__file__])


||||||| base
=======
import pytest
import logging
import sys
from src.agents.blockchain.network_agent import NetworkAgent

@pytest.fixture
async def network_agent():
    agent = NetworkAgent(max_peers=3)
    await agent.start()
    yield agent
    await agent.stop()

@pytest.mark.asyncio
async def test_basic_functionality(network_agent):
    # Test peer connection
    peer1 = {
        'peer_id': 'test_peer_1',
        'address': '127.0.0.1',
        'port': 8000
    }
    success = await network_agent.connect_peer({'type': 'connect_peer', **peer1})
    assert success
    
    # Test broadcasting a transaction
    tx_task = {
        'type': 'broadcast_transaction',
        'transaction': {
            'from': 'wallet1',
            'to': 'wallet2',
            'amount': 1.0
        }
    }
    result = await network_agent.process_task(tx_task)
    assert result['status'] == 'success'
    
    # Test peer info retrieval
    info_task = {'type': 'get_peer_info'}
    result = await network_agent.process_task(info_task)
    assert len(result['result']['peers']) == 1

@pytest.mark.asyncio
async def test_max_peers(network_agent):
    # Try to connect more peers than max_peers
    for i in range(5):  # More than max_peers (3)
        peer = {
            'peer_id': f'test_peer_{i}',
            'address': '127.0.0.1',
            'port': 8000 + i
        }
        await network_agent.connect_peer({'type': 'connect_peer', **peer})
    
    # Verify peer count
    info_task = {'type': 'get_peer_info'}
    result = await network_agent.process_task(info_task)
    assert len(result['result']['peers']) == 3  # Should be limited to max_peers

@pytest.mark.asyncio
async def test_network_messages(network_agent):
    # Connect a peer
    peer1 = {
        'peer_id': 'test_peer_1',
        'address': '127.0.0.1',
        'port': 8000
    }
    await network_agent.connect_peer({'type': 'connect_peer', **peer1})
    
    # Test block broadcasting
    block_task = {
        'type': 'broadcast_block',
        'block': {
            'index': 1,
            'timestamp': '2024-12-20T21:00:00Z',
            'transactions': []
        }
    }
    result = await network_agent.process_task(block_task)
    assert result is not None
    
    # Test sync request
    sync_task = {
        'type': 'sync_request',
        'peer_id': 'test_peer_1',
        'start_block': 0,
        'end_block': 10
    }
    result = await network_agent.process_task(sync_task)
    assert result is not None

if __name__ == '__main__':
    pytest.main([__file__])
>>>>>>> theirs
