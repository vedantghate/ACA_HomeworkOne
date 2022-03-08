class Node:
    def __init__(self, left=None, right=None, parent=None):
        self._left = left
        self._right = right
        self.parent = None
        self.bit = -1
        self._block = None  # Only applicable for leaf nodes
        self.hashMap = {}

    @property
    def block(self):
        if self._block is None:
            raise Exception("Not yet populated")
        return self._block

    @block.setter
    def block(self, blockVal):
        if self.left or self.right:
            raise Exception("Block assigning not allowed")
        self._block = blockVal

    @property
    def left(self):
        if self._left is None:
            raise Exception("Not yet populated")
        return self._left

    @left.setter
    def left(self, node):
        # Union node.hashMap & self.hashMap
        self._left = node
        self.hashMap = unionMap


class Leaf:
    def __init__(self, tag):
        self.tag = tag
