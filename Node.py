class Node:
    def __init__(self, node_id, left=None, right=None, parent=None):
        self._left = left
        self._right = right
        self.parent = parent
        self.node_id = node_id
        self.bit = 0
        self._block = None  # Only applicable for leaf nodes
        self.hashMap = {}

    @property
    def block(self):
        if self._block is None:
            pass  # raise Exception("Not yet populated")
        return self._block

    @block.setter
    def block(self, block_val):
        if self.left or self.right:
            raise Exception("Block assigning not allowed")
        self._block = block_val

    @property
    def left(self):
        if self._left is None:
            pass  # raise Exception("Not yet populated")
        return self._left

    @left.setter
    def left(self, node):
        self._left = node

    @property
    def right(self):
        if self._right is None:
            pass  # raise Exception("Not yet populated")
        return self._right

    @right.setter
    def right(self, node):
        self._right = node


class Leaf:
    def __init__(self, tag):
        self.tag = tag
