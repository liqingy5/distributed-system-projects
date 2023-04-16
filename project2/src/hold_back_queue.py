class HoldBackQueue:
    def __init__(self):
        self.queue = []

    def isEmpty(self):
        return len(self.queue) == 0

    # for inserting an element in the queue
    def push(self, vector, data):
        self.queue.append((vector, data))
        self.queue = sorted(self.queue, key=lambda x: sum(x[0]))
        print()
        print(vector)
        self.printQueue()

    # for popping an element based on Priority
    def pop(self):
        if (self.isEmpty()):
            return None
        return self.queue.pop(0)

    def front(self):
        if (self.isEmpty()):
            return None
        return self.queue[0]

    def clear(self):
        self.queue.clear()

    def printQueue(self):
        print()
        print("Queue")
        for ele in self.queue:
            print(f"vector {ele[0]} data {ele[1]} ")
        print("Queue end")
        print()
