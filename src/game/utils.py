class AsyncEvent:
    def __init__(self):
        self.subscribers = set()

    def subscribe(self, subscriber: callable):
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber: callable):
        self.subscribers.remove(subscriber)

    async def trigger(self, *args, **kwargs):
        print(f"Triggering event with {len(self.subscribers)} subscribers")
        for subscriber in self.subscribers:
            await subscriber(*args, **kwargs)
