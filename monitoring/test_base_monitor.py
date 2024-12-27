import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from .base_monitor import BaseMonitor, MetricType, MetricDefinition

class TestMonitor(BaseMonitor):
    """Test implementation of BaseMonitor for testing"""
    def __init__(self):
        super().__init__()
        self.metrics = {}
        self.system_metrics_enabled = False
        self._is_monitoring = False

    async def collect_metrics(self):
        """Test implementation of metric collection"""
        return {
            "test.metric": 100,
            "test.counter": 1
        }

    async def check_health(self):
        """Test implementation of health check"""
        return True

    async def initialize(self):
        """Initialize the test monitor"""
        self._is_monitoring = False
        self.metrics = {}

    async def cleanup(self):
        """Cleanup resources"""
        self._is_monitoring = False
        self.metrics = {}

@pytest_asyncio.fixture
async def test_monitor():
    """Fixture to provide a test monitor instance"""
    monitor = TestMonitor()
    await monitor.initialize()
    try:
        return monitor
    finally:
        await monitor.cleanup()

@pytest.fixture
def mock_alert_manager():
    """Fixture to provide a mock alert manager"""
    return Mock()

@pytest.mark.asyncio
async def test_metric_registration(test_monitor):
    """Test metric registration functionality"""
    # Register a test metric (removed await since it's not async)
    test_monitor.register_metric(
        name="test.metric",
        metric_type=MetricType.GAUGE,
        description="Test metric",
        unit="count",
        thresholds={"HIGH": 150}
    )
    
    assert "test.metric" in test_monitor.metric_definitions
    metric_def = test_monitor.metric_definitions["test.metric"]
    assert metric_def.type == MetricType.GAUGE
    assert metric_def.unit == "count"
    assert metric_def.thresholds == {"HIGH": 150}

@pytest.mark.asyncio
async def test_metric_collection(test_monitor):
    """Test basic metric collection"""
    collected = False
    
    async def callback(metrics, health):
        nonlocal collected
        collected = True
        assert "test.metric" in metrics
        assert metrics["test.metric"] == 100
        assert health is True
    
    # Start monitoring without timeout
    monitoring_task = asyncio.create_task(
        test_monitor.start_monitoring(callback)
    )
    
    try:
        # Give it time to run one collection cycle
        await asyncio.sleep(0.2)
        assert collected
    finally:
        await test_monitor.stop_monitoring()
        await monitoring_task

@pytest.mark.asyncio
async def test_system_metrics_collection(test_monitor):
    """Test system metrics collection"""
    # Removed await since these aren't async methods
    test_monitor.enable_system_metrics()
    test_monitor.register_system_metrics()
    
    metrics = await test_monitor.collect_system_metrics()
    
    # Verify essential system metrics are present
    assert "system.cpu.percent" in metrics
    assert "system.memory.percent" in metrics
    assert "system.disk.percent" in metrics
    assert "system.network.bytes_sent" in metrics
    assert "system.network.bytes_recv" in metrics

@pytest.mark.asyncio
async def test_threshold_monitoring(test_monitor, mock_alert_manager):
    """Test threshold monitoring and alerting"""
    # Set up the alert manager
    test_monitor.alert_manager = mock_alert_manager
    
    # Configure mock
    mock_alert_manager.create_alert = Mock()
    mock_alert_manager.create_alert.return_value = None
    
    # Register metric with threshold
    test_monitor.register_metric(
        name="test.metric",
        metric_type=MetricType.GAUGE,
        description="Test metric",
        unit="count",
        thresholds={"HIGH": 50}  # Threshold is 50, we'll send 100
    )
    
    # Process metrics that should trigger the alert
    await test_monitor.process_metrics({"test.metric": 100})
    
    # Give a small delay for async operations
    await asyncio.sleep(0.1)
    
    # Verify alert was created
    mock_alert_manager.create_alert.assert_called_once()
    
    # Check alert details
    call_args = mock_alert_manager.create_alert.call_args[1]
    assert call_args["severity"] == "HIGH"
    assert "test.metric" in call_args["metrics"]
    assert call_args["metrics"]["test.metric"] == 100

@pytest.mark.asyncio
async def test_metric_history(test_monitor):
    """Test metric history storage and retrieval"""
    # Register the metric first
    test_monitor.register_metric(
        name="test.metric",
        metric_type=MetricType.GAUGE,
        description="Test metric",
        unit="count",
        thresholds={}
    )
    
    # Process some test metrics
    for _ in range(3):
        await test_monitor.process_metrics({"test.metric": 100})
        await asyncio.sleep(0.1)
    
    # Get metric history
    history = await test_monitor.get_metric_history("test.metric")
    
    assert len(history) == 3
    assert all(m["value"] == 100 for m in history)
    assert all("timestamp" in m for m in history)

@pytest.mark.asyncio
async def test_counter_metrics(test_monitor):
    """Test counter metric type handling"""
    test_monitor.register_metric(
        name="test.counter",
        metric_type=MetricType.COUNTER,
        description="Test counter",
        unit="count",
        thresholds={}
    )
    
    # Process incremental counter values
    await test_monitor.process_metrics({"test.counter": 5})
    await test_monitor.process_metrics({"test.counter": 3})
    
    # Get metric history
    history = await test_monitor.get_metric_history("test.counter")
    
    assert len(history) == 2
    assert history[0]["value"] == 5
    assert history[1]["value"] == 3
    assert history[1]["cumulative_value"] == 8

@pytest.mark.asyncio
async def test_metric_statistics(test_monitor):
    """Test statistical calculations for metrics"""
    test_monitor.register_metric(
        name="test.stats",
        metric_type=MetricType.HISTOGRAM,
        description="Test histogram",
        unit="ms",
        thresholds={}
    )
    
    # Process various values
    values = [10, 20, 30, 40, 50]
    for value in values:
        await test_monitor.process_metrics({"test.stats": value})
    
    # Get statistics - changed to await if get_metric_statistics is async
    stats = await test_monitor.get_metric_statistics("test.stats")
    
    assert stats["count"] == 5
    assert stats["min"] == 10
    assert stats["max"] == 50
    assert stats["mean"] == 30
    assert stats["median"] == 30
    assert stats["p90"] == 50
    assert "stddev" in stats

@pytest.mark.asyncio
async def test_error_handling(test_monitor, mock_alert_manager):
    """Test error handling during metric collection"""
    test_monitor.alert_manager = mock_alert_manager
    
    # Simulate an error during collection
    error = Exception("Test error")
    await test_monitor.handle_collection_error(error)
    
    # Verify error alert was created
    mock_alert_manager.create_alert.assert_called_once()
    call_args = mock_alert_manager.create_alert.call_args[1]
    assert call_args["severity"] == "HIGH"
    assert "Test error" in call_args["message"]

# Adding new test for monitoring status
@pytest.mark.asyncio
async def test_monitoring_status(test_monitor):
    """Test monitoring status management"""
    assert not test_monitor._is_monitoring
    
    async def callback(metrics, health):
        pass
    
    monitoring_task = asyncio.create_task(
        test_monitor.start_monitoring(callback)
    )
    
    try:
        await asyncio.sleep(0.1)
        assert test_monitor._is_monitoring
        
        await test_monitor.stop_monitoring()
        assert not test_monitor._is_monitoring
    finally:
        if not monitoring_task.done():
            await test_monitor.stop_monitoring()
            await monitoring_task

# Adding new test for metric validation
@pytest.mark.asyncio
async def test_metric_validation(test_monitor):
    """Test metric validation logic"""
    # Test invalid metric registration
    with pytest.raises(ValueError):
        test_monitor.register_metric(
            name="invalid.metric",
            metric_type="INVALID_TYPE",
            description="Invalid metric",
            unit="count",
            thresholds={}
        )
    
    # Test invalid threshold format
    with pytest.raises(ValueError):
        test_monitor.register_metric(
            name="invalid.threshold",
            metric_type=MetricType.GAUGE,
            description="Invalid threshold",
            unit="count",
            thresholds={"INVALID": "not a number"}
        )