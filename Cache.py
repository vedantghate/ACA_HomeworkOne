import math
import Block
import Node


class Cache:
    def __init__(self, size, associativity, block_size, inclusion_property, replacement_policy):
        self.associativity = associativity
        self.size = size
        self.block_size = block_size
        self.num_of_sets = 0
        self.number_of_tag_bits = 0
        self.number_of_index_bits = 0
        self.number_of_offset_bits = 0
        self.block_container = []
        self.timestamp = -math.inf
        self.inclusion_property = inclusion_property
        self.replacement_policy = replacement_policy
        self.future_table = {}
        self.plru_trees = {}
        self.measurements = {
            "reads": 0,
            "reads_miss": 0,
            "writes": 0,
            "writes_miss": 0,
            "miss_rate": 0,
            "num_writebacks": 0,
            "memory_traffic": 0
        }
        self.build_cache()

    def build_cache(self):
        """
        Builds the cache container by initializing the required number of blocks.
        The number of block will be given by get_dimensions() method.
        The container will contain 'num_of_sets' rows and 'associativity' columns,
        where each cell will hold an object of the class Block.
        :return: A m * n matrix where, m = num_of_sets and n = associativity
        """
        self.get_dimensions()  # get dimensions
        for i in range(self.num_of_sets):
            i_set = []
            if self.replacement_policy == 1:
                # create Trees here
                height = math.log(self.associativity, 2) - 1 # TODO check +- 1
                i_set.append(self.createTree(height))
            else:
                for j in range(self.associativity):
                    block = Block.Block()
                    i_set.append(block)
            self.block_container.append(i_set)

    def read(self, instruction):
        """
        Reads the instruction tag in the set of cache given by the index of the instruction.
        The index and tag will be determined by making a call to the method get_instruction_components.
        :return: An integer flag which will indicate whether the read operation resulted
        in a hit, a miss or a miss-replace. (0, 1, 2 respectively)
        """
        index, tag = self.get_instruction_components(instruction)
        for block in self.block_container[index]:
            if block.tag == tag:
                block.time = self.timestamp
                return 0
            elif block.tag == "":
                block.tag = tag
                block.time = self.timestamp
                return 1
            else:
                pass
        self.evict(index, tag, 'r')
        return 2

    def write(self, instruction):
        """
        Writes the instruction tag to the block in a set of cache given by the index of the instruction.
        The index and tag will be determined by making a call to the method get_instruction_components.
        :return: A boolean flag which will indicate whether the write operation resulted in a hit or a miss.
        """
        index, tag = self.get_instruction_components(instruction)
        for block in self.block_container[index]:
            if block.tag == tag:
                block.isDirty = True
                block.time = self.timestamp
                return 0
            elif block.tag == "":
                block.tag = tag
                block.isDirty = True
                block.time = self.timestamp
                return 1
            else:
                pass
        self.evict(index, tag, 'w')  # the isDirty flag of evicted block should be set to false
        return 2

    def evict(self, index, tag, mode):
        """
        Evicts a block from the cache.
        In case of a miss and replace, this method will determine the block to be evicted
        following the replacement policy provided to the cache.
        0 for LRU, 1 for Pseudo-LRU, 2 for Optimal.
        :return: NONE
        """
        block_set = self.block_container[index]
        if self.replacement_policy == 0:
            self.evictLRU(block_set, tag, self.timestamp, mode)
        elif self.replacement_policy == 1:
            self.evictPLRU(block_set, tag, self.timestamp, mode)
        else:
            self.evictOPT(block_set, tag, self.timestamp, mode, index)

    def execute(self, instruction):
        """
        Executes a read/write as specified in the instruction
        and performs a counter update.
        :return: updates the value to the 'timestamp'
        """
        if self.timestamp < 0:
            self.timestamp = 0
        else:
            self.timestamp += 1

        index, tag = self.get_instruction_components(instruction[1])

        if instruction[0] == 'r':
            status = self.plru(tag, index) if self.replacement_policy == 1 else self.read(instruction[1])
            self.measurements['reads'] += 1
            if status == 0:
                pass
            elif status == 1:
                self.measurements['reads_miss'] += 1
            else:
                self.measurements['reads_miss'] += 1
        else:
            status = self.plru(tag, index) if self.replacement_policy == 1 else self.write(instruction[1])
            self.measurements['writes'] += 1
            if status == 0:
                pass
            elif status == 1:
                self.measurements['writes_miss'] += 1
            else:
                self.measurements['writes_miss'] += 1

        if self.replacement_policy == 2:
            self.future_table[index].pop(0)

    def get_dimensions(self):
        """
        Calculates the dimensions of the cache container, and the #index bits, offset bits and tag bits
        by using #sets = size / (associativity * block size), #index bits = log(#sets)(base2),
        #offset bits = log(blocksize) and #tag bits = 32 - [#index bits + #offset bits]
        :return: num_of_sets in the cache,
        """
        self.num_of_sets = int(self.size / (self.associativity * self.block_size))
        self.number_of_index_bits = int(math.log(self.num_of_sets, 2))
        self.number_of_offset_bits = int(math.log(self.block_size, 2))
        self.number_of_tag_bits = 32 - (self.number_of_index_bits + self.number_of_offset_bits)

    def get_instruction_components(self, instruction):
        """
        The instruction received by the cache will be a 32 bit hex instruction.
        To perform operations on the cache, we need to separate its components
        and determine the index and tag for the operation.
        :return: index of the cache at which the operation is to be done.
                 tag of the instruction.
        """
        binary_instruction = str(bin(int(instruction, base=16)))[2:].zfill(32)

        index = int(binary_instruction[self.number_of_tag_bits:32 - self.number_of_offset_bits], 2)
        tag = "0x" + '{:0{}x}'.format(int(binary_instruction[:self.number_of_tag_bits], 2),
                                      int(self.number_of_tag_bits / 4))
        return index, tag

    def getMissRate(self, cache_level):
        if cache_level == 1:
            self.measurements['miss_rate'] = (self.measurements['reads_miss'] + self.measurements['writes_miss']) \
                                                 / (self.measurements['reads'] + self.measurements['writes'])

    def getMemoryTraffic(self, cache_level, higher_level_direct_writebacks):
        if cache_level == 1:
            self.measurements['memory_traffic'] = self.measurements['num_writebacks'] + self.measurements['reads_miss']\
                                                  + self.measurements['writes_miss']
        else:
            self.measurements['memory_traffic'] = self.measurements['num_writebacks'] + self.measurements['reads_miss'] \
                                                  + self.measurements['writes_miss']
            if self.inclusion_property == 1:
                # add direct writebacks to memory of higher level cache in case of inclusion
                self.measurements['memory_traffic'] += higher_level_direct_writebacks


    def display_cache_content(self):
        print("============= START OF CACHE ===============")
        for i in range(self.num_of_sets):
            print("Set:", i, " ")
            for j in range(self.associativity):
                dirty = "D" if self.block_container[i][j].isDirty else ""
                print(self.block_container[i][j].tag, dirty,
                      # self.block_container[i][j].time,
                      end=" | ")
            print("")
            for j in range(self.associativity):
                print("____________", end="_")
            print("")
        print("============= END OF CACHE ================")

    # ================================== Eviction Policies ==================================
    def evictLRU(self, block_set, tag, time, mode):
        min_index = block_set.index(min(block_set, key=lambda x: x.time))
        block_set[min_index].tag = tag
        block_set[min_index].time = time

        if block_set[min_index].isDirty:
            self.measurements['num_writebacks'] += 1  # if block is dirty, write-back will be issued

        if mode == 'r':
            block_set[min_index].isDirty = False
        else:
            block_set[min_index].isDirty = True

    def evictPLRU(self, block_set, tag, time, mode):
        pass

    def evictOPT(self, block_set, tag, time, mode, index):
        if len(self.future_table[index]) > 0:
            timestamp_dict = {}
            for i in block_set:
                j = 0
                while i.tag != self.future_table[index][j]:
                    j += 1
                    if j >= len(self.future_table[index]):
                        timestamp_dict[i.tag] = math.inf
                        break
                timestamp_dict[i.tag] = j
            tag_to_evict = max(timestamp_dict, key=timestamp_dict.get)
            for block in block_set:
                if block.tag == tag_to_evict:
                    block.tag = tag
                    block.time = time

                    if block.isDirty:
                        self.measurements['num_writebacks'] += 1  # if block is dirty, write-back will be issued

                    if mode == 'r':
                        block.isDirty = False
                    else:
                        block.isDirty = True
                    break
        else:
            block_set[0].tag = tag
            block_set[0].time = time

            if block_set[0].isDirty:
                self.measurements['num_writebacks'] += 1  # if block is dirty, write-back will be issued

            if mode == 'r':
                block_set[0].isDirty = False
            else:
                block_set[0].isDirty = True

    def createTree(self, height):
        root = Node.Node()
        stack = [root]
        for i in range(height):
            for j in range(2 ** i):
                tempNode = stack.pop(0)
                leftNode = Node.Node()
                rightNode = Node.Node()
                tempNode.left = leftNode
                tempNode.right = rightNode
                stack.extend([leftNode, rightNode])

        self.populateTree(root)
        return root

    def populateTree(self, root):
        stack = [root]
        while stack:
            node = stack.pop(0)
            if node.left is None and node.right is None:
                # create block here
                block = Block.Block()
                node.block = block
                continue
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)

    def updateTree(self, root, mode="a"):
        """
        mode = a => access
               r => replace
        """
        node = root
        while(node.block is None):
            if node.bit == 0:
                nextNode = node.left if mode == "a" else node.right
            else:
                nextNode = node.right if mode == "a" else node.left
            node.bit = 0 if node.bit else 1
            node = nextNode
        return node


    def plru(self, tag, index):
        root = self.plru_trees[index] if index in self.plru_trees.keys() else Node.Node()
        temp = root # copy.deepcopy(root)
        height = int(math.log(self.associativity, 2)) - 1
        print("===> height: ", height)
        for i in range(height):
            if temp.left is None:
                temp.left = Node.Node()
                temp.bit = 0
                temp = temp.left
            elif temp.right is None:
                temp.right = Node.Node()
                temp.bit = 1
                temp = temp.right

        if temp.left is None:
            temp.left = Node.Leaf(tag)
            temp.bit = 0
        elif temp.right is None:
            temp.right = Node.Leaf(tag)
            temp.bit = 1
        self.plru_trees[index] = root
        print("========== Tree ===============")
        self.print_tree(root)
        print("===============================")

    def print_tree(self, root):
        if isinstance(root, Node.Node):
            if root.left:
                self.print_tree(root.left)
            print(root.bit)
            if root.right:
                self.print_tree(root.right)
        else:
            print(root.tag)

class PLRUCache(Cache):
    def __init__(self, *args, **kwargs):
        super(PLRUCache, self).__init__(*args, **kwargs)

    def read(self, instruction):
        index, tag = self.get_instruction_components(instruction)
        self.updateTree(self.block_container[index], mode="a")

