# TDA Cola (FIFO)
"""
Se define una clase Cola. Esta estructura es clave para gestionar
las misiones de cada personaje de forma ordenada: la primera misión en entrar será la primera en salir (FIFO).
"""
class Cola:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def first(self):
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)