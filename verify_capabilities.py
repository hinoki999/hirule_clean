from src.agents.base import AgentCapability

def verify_capabilities():
    assert hasattr(AgentCapability, "TRADING"), "TRADING capability is missing"
    assert hasattr(AgentCapability, "MARKET_DATA"), "MARKET_DATA capability is missing"
    assert hasattr(AgentCapability, "ORDER_MANAGEMENT"), "ORDER_MANAGEMENT capability is missing"
    print("All trading capabilities are present")


