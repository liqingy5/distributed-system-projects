import heapq


class HoldBackQueue:
    def __init__(self):
        self.queue = []
        self.index = 0

    def isEmpty(self):
        return len(self.queue) == 0

    def compare(self, a, b):
        return

    # for inserting an element in the queue
    def push(self, i, data):
        heapq.heappush(self.queue, (i, self.index, data))
        self.index += 1

    # for popping an element based on Priority
    def pop(self):
        return heapq.heappop(self.queue)

    def front(self):
        return self.queue[0]

    def printQueue(self):
        for ele in self.queue:
            print(f"vector {ele[0]} index {ele[1]} data {ele[2]}")
