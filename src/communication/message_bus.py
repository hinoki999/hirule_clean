class MessageBus:
    def __init__(self):
        self.subscribers = {}
    
    async def subscribe(self, topic: str, callback):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
