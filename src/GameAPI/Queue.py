class Queue:
    def __init__(self):
        self.queue = []

    def put(self, item):
        self.queue.append(item)

    def get(self):
        return_value = self.queue[0]
        self.remove(self.queue[0])
        return return_value

    def remove(self, value):
        self.queue.remove(value)

    def remove_by_index(self, index):
        value = self.queue[index]
        self.remove(value)

    def index(self, value):
        return self.queue.index(value)

    def __len__(self):
        return len(self.queue)

    def __contains__(self, item):
        return self.queue.__contains__(item)