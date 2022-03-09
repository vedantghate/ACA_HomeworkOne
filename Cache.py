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
        self.is_write_back = False
        self.write_back_inst = ""
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
                height = int(math.log(self.associativity, 2))
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
                block.instruction = instruction
                block.time = self.timestamp
                return 1
            else:
                pass
        self.evict(index, tag, 'r', instruction)
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
                block.instruction = instruction
                block.isDirty = True
                block.time = self.timestamp
                return 1
            else:
                pass
        self.evict(index, tag, 'w', instruction)  # the isDirty flag of evicted block should be set to false
        return 2

    def evict(self, index, tag, mode, instruction):
        """
        Evicts a block from the cache.
        In case of a miss and replace, this method will determine the block to be evicted
        following the replacement policy provided to the cache.
        0 for LRU, 1 for Pseudo-LRU, 2 for Optimal.
        :return: NONE
        """
        block_set = self.block_container[index]
        if self.replacement_policy == 0:
            self.evictLRU(block_set, tag, self.timestamp, mode, instruction)
        elif self.replacement_policy == 1:
            self.evictPLRU(block_set, tag, self.timestamp, mode)
        else:
            self.evictOPT(block_set, tag, self.timestamp, mode, index, instruction)

    def execute(self, instruction):
        """
        Executes a read/write as specified in the instruction
        and performs a counter update. Updates the value to the 'timestamp'
        :return: Status of the read/write operation
        0 - hit, 1 miss, 2 miss-replace
        """
        if self.timestamp < 0:
            self.timestamp = 0
        else:
            self.timestamp += 1

        self.is_write_back = False
        self.write_back_inst = ""

        index, tag = self.get_instruction_components(instruction[1])

        if instruction[0] == 'r':
            status = self.read(instruction[1])
            self.measurements['reads'] += 1
            if status == 0:
                pass
            elif status == 1:
                self.measurements['reads_miss'] += 1
            else:
                self.measurements['reads_miss'] += 1
        else:
            status = self.write(instruction[1])
            self.measurements['writes'] += 1
            if status == 0:
                pass
            elif status == 1:
                self.measurements['writes_miss'] += 1
            else:
                self.measurements['writes_miss'] += 1
        if self.replacement_policy == 2:
            self.future_table[index].pop(0)
        return status

    def issue_writeback(self, instruction):
        self.is_write_back = True
        self.write_back_inst = instruction

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
            self.measurements['memory_traffic'] = self.measurements['num_writebacks'] + self.measurements['reads_miss'] \
                                                  + self.measurements['writes_miss']
        else:
            self.measurements['memory_traffic'] = self.measurements['num_writebacks'] + self.measurements['reads_miss'] \
                                                  + self.measurements['writes_miss']
            if self.inclusion_property == 1:
                # add direct writebacks to memory of higher level cache in case of inclusion
                self.measurements['memory_traffic'] += higher_level_direct_writebacks

    def display_cache_content(self):
        for i in range(self.num_of_sets):
            print("Set", i, ":", end=" ")
            for j in range(self.associativity):
                dirty = "D" if self.block_container[i][j].isDirty else ""
                print(self.block_container[i][j].tag[2:], dirty,
                      # self.block_container[i][j].time,
                      end=" ")
            print("")

    # ================================== Eviction Policies ==================================
    def evictLRU(self, block_set, tag, time, mode, instruction):
        min_index = block_set.index(min(block_set, key=lambda x: x.time))
        block_set[min_index].tag = tag
        block_set[min_index].time = time

        if block_set[min_index].isDirty:
            self.measurements['num_writebacks'] += 1  # if block is dirty, write-back will be issued
            self.issue_writeback(block_set[min_index].instruction)
        block_set[min_index].instruction = instruction
        if mode == 'r':
            block_set[min_index].isDirty = False
        else:
            block_set[min_index].isDirty = True

    def evictPLRU(self, block_set, tag, time, mode):
        pass

    def evictOPT(self, block_set, tag, time, mode, index, instruction):
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
                        self.issue_writeback(block.instruction)
                    block.instruction = instruction

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
                self.issue_writeback(block_set[0].instruction)

            block_set[0].instruction = instruction

            if mode == 'r':
                block_set[0].isDirty = False
            else:
                block_set[0].isDirty = True

    # ================================= PLRU ==============================
    def createTree(self, height):
        root = Node.Node(0)
        stack = [root]
        node_id_counter = 1
        for i in range(height):
            for j in range(2 ** i):
                tempNode = stack.pop(0)

                leftNode = Node.Node(node_id_counter, parent=tempNode)
                node_id_counter += 1

                rightNode = Node.Node(node_id_counter, parent=tempNode)
                node_id_counter += 1

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

    def updateTree(self, root, tag, r_w, instruction, mode="r"):
        """
        mode = a => access
               r => replace
        :return: The leaf node
        """
        node = root
        while node.block is None:
            if node.bit == 0:
                nextNode = node.left if mode == "a" else node.right
            else:
                nextNode = node.right if mode == "a" else node.left
            node.bit = 0 if node.bit else 1
            node = nextNode

        if mode == 'r':
            node.block.tag = tag
            if node.block.isDirty:
                self.measurements['num_writebacks'] += 1
                self.issue_writeback(node.block.instruction)

            node.block.instruction = instruction

            if r_w == 'w':
                node.block.isDirty = True
            else:
                node.block.isDirty = False
        return node

    def update_hit_tree(self, root, path_to_leaf, mode):
        tempNode = root
        for i in range(len(path_to_leaf) - 1):
            if tempNode.block is None:
                if tempNode.left.node_id == path_to_leaf[i+1]:
                    tempNode.bit = 0
                    tempNode = tempNode.left
                else:
                    tempNode.bit = 1
                    tempNode = tempNode.right
        if mode == 'w':
            tempNode.block.isDirty = True

    def print_tree(self, root):
        if root.block is None:
            print("Node ID: ", root.node_id, "Bit: ", root.bit)
        if root.left:
            self.print_tree(root.left)
        if root.right:
            self.print_tree(root.right)
        if root.block is not None:
            print("Node ID: ", root.node_id, "Tag: => ", root.block.tag)

    def get_leaf_nodes(self, root, leaf_set):
        if root.block is None:
            pass
        if root.left:
            self.get_leaf_nodes(root.left, leaf_set)
        if root.right:
            self.get_leaf_nodes(root.right, leaf_set)
        if root.block is not None:
            if root.block.tag != "":
                leaf_set.append(root)
        return leaf_set

    def get_path(self, leaf):
        path = [leaf.node_id]
        tempNode = leaf
        while tempNode.parent is not None:
            path.append(tempNode.parent.node_id)
            tempNode = tempNode.parent
        path.reverse()
        return path


class PLRUCache(Cache):
    def __init__(self, *args, **kwargs):
        super(PLRUCache, self).__init__(*args, **kwargs)

    def read(self, instruction):
        index, tag = self.get_instruction_components(instruction)

        root = self.block_container[index][0]
        leaf_set = self.get_leaf_nodes(root, [])

        if len(leaf_set) < self.associativity:
            self.updateTree(root, tag, 'r', instruction)
            return 1
        elif tag in [x.block.tag for x in leaf_set]:
            path_to_leaf = []
            for leaf in leaf_set:
                if leaf.block.tag == tag:
                    path_to_leaf = self.get_path(leaf)
                    break
            self.update_hit_tree(root, path_to_leaf, 'r')
            return 0
        else:
            self.updateTree(root, tag, 'r', instruction)
            return 2

    def write(self, instruction):
        index, tag = self.get_instruction_components(instruction)

        root = self.block_container[index][0]
        leaf_set = self.get_leaf_nodes(root, [])

        if len(leaf_set) < self.associativity:
            self.updateTree(root, tag, 'w', instruction)
            return 1
        elif tag in [x.block.tag for x in leaf_set]:
            path_to_leaf = []
            for leaf in leaf_set:
                if leaf.block.tag == tag:
                    path_to_leaf = self.get_path(leaf)
                    break
            self.update_hit_tree(root, path_to_leaf, 'w')
            return 0
        else:
            self.updateTree(root, tag, 'w', instruction)
            return 2

    def display_cache_content(self):
        for i in range(self.num_of_sets):
            print("Set", i, ":", end=" ")
            leaf_set = self.get_leaf_nodes(self.block_container[i][0], [])
            for j in range(len(leaf_set)):
                dirty = "D" if leaf_set[j].block.isDirty else ""
                print(leaf_set[j].block.tag[2:], dirty,
                      # self.block_container[i][j].time,
                      end=" ")
            print("")