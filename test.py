import math
import random


def evictLRU(block_set, tag, time, mode):
    block_set.sort(key=lambda x: x.time)
    block_set[0].tag = tag
    block_set[0].time = time
    if mode == 'w':
        block_set[0].isDirty = True
    for j in block_set:
        print(j.time, j.tag)

def evictOPT(block_set, tag, time, mode):
    pass


class Block:
    def __init__(self):
        self.tag = ""
        self.time = -math.inf
        self.isDirty = False


blkst = []
for i in range(5):
    block = Block()
    block.time = i
    block.tag = str(str(i)+str(i)+str(i)+str(i)+str(i)+str(i))
    blkst.append(block)
random.shuffle(blkst)
for i in range(5):
    print(blkst[i].time, blkst[i].tag)


evictLRU(blkst, "555555", 5, 'r')
evictLRU(blkst, "666666", 6, 'r')



