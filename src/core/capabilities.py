class Capability:
    """Base class for all capabilities"""
    name = "base_capability"
    version = "1.0.0"
    
    def __init__(self):
        self.required_capabilities = []
