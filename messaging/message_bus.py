class Message:
    def __init__(self, id=None, sender=None, recipient=None, message_type=None, payload=None, priority=0):
        self.id = id
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.payload = payload
        self.priority = priority


class MessageBus:
    def __init__(self):
        self.subscribers = {}

    async def subscribe(self, topic: str, callback):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def publish(self, message):
        # Basic implementation
        return True

    async def get_messages(self, topic):
        # Basic implementation
        return None

    def create_message(self, sender, recipient, message_type, payload, priority=0):
        return Message(sender=sender, recipient=recipient, message_type=message_type, 
                      payload=payload, priority=priority)
