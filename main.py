import Cache

instruction_queue = []


def read_tracefile():
    f = open("/Users/jarvis/MS CS/Spring 22/ACA/AssignmentOne/Traces/gcc_trace.txt", "r")
    for x in f:
        inst = x.rstrip().split(' ')
        if len(inst) == 2:
            instruction_queue.append(inst)


def generate_future_dict(cache_l: Cache.Cache):
    address_dict = {}
    for ins in instruction_queue:
        idx, tag = cache_l.get_instruction_components(ins[1])
        if idx not in address_dict.keys():
            address_dict[idx] = [tag]
        else:
            address_dict[idx].append(tag)
    cache_l.future_table = address_dict


def run_PLRU():
    plru_cache = Cache.PLRUCache(size=1024, associativity=2, inclusion_property=0, replacement_policy=1, block_size=16)
    for inst in instruction_queue:
        plru_cache.execute(inst)
    plru_cache.display_cache_content()
    plru_cache.getMissRate(1)
    plru_cache.getMemoryTraffic(1, 0)
    print(plru_cache.measurements)


def run_LRU():
    l1_cache = Cache.Cache(size=1024, associativity=2, inclusion_property=0, replacement_policy=0, block_size=16)
    for inst in instruction_queue:
        l1_cache.execute(inst)
    l1_cache.display_cache_content()
    l1_cache.getMissRate(1)
    l1_cache.getMemoryTraffic(1, 0)
    print(l1_cache.measurements)


def run_OPT():
    l1_cache = Cache.Cache(size=1024, associativity=2, inclusion_property=0, replacement_policy=2, block_size=16)
    generate_future_dict(l1_cache)
    for inst in instruction_queue:
        l1_cache.execute(inst)
    l1_cache.display_cache_content()
    l1_cache.getMissRate(1)
    l1_cache.getMemoryTraffic(1, 0)
    print(l1_cache.measurements)


read_tracefile()
print("======== Pseudo LRU ========")
run_PLRU()
print("=========== LRU ============")
run_LRU()
print("=========== OPT ============")
run_OPT()
