import sys
import Cache


def configurator():
    '''
    Parses the command and extracts the configuration parameters from it
    <BLOCKSIZE> <L1_SIZE> <L1_ASSOC> <L2_SIZE> <L2_ASSOC>
    <REPLACEMENT_POLICY> <INCLUSION_PROPERTY> <trace_file>
    0 for LRU, 1 for PLRU, 2 for Optimal.
    0 for non-inclusive, 1 for inclusive.
    :return: The configuration parameters
    '''
    parameters = sys.argv
    blocksize = int(parameters[1])
    l1size = int(parameters[2])
    l1assoc = int(parameters[3])
    l2size = int(parameters[4])
    l2assoc = int(parameters[5])
    rep_pol = int(parameters[6])
    inc_pol = int(parameters[7])
    file = parameters[8]

    return blocksize, l1size, l1assoc, l2size, l2assoc, rep_pol, inc_pol, file


def read_tracefile(path):
    f = open(path, "r")
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
    plru_cache_l1 = Cache.PLRUCache(size=l1size, associativity=l1assoc, inclusion_property=inc_pol,
                                    replacement_policy=rep_pol, block_size=blocksize)
    if l2size:
        plru_cache_l2 = Cache.PLRUCache(size=l2size, associativity=l2assoc, inclusion_property=inc_pol,
                                        replacement_policy=rep_pol, block_size=blocksize)
    for inst in instruction_queue:
        status = plru_cache_l1.execute(inst)
        if l2size:
            if plru_cache_l1.is_write_back:
                plru_cache_l2.execute(['w', plru_cache_l1.write_back_inst])
            if status != 0:
                plru_cache_l2.execute(['r', inst[1]])
    print("===== L1 contents =====")
    plru_cache_l1.display_cache_content()
    if l2size:
        print("===== L2 contents =====")
        plru_cache_l2.display_cache_content()
    plru_cache_l1.getMissRate(1)
    plru_cache_l1.getMemoryTraffic(1, 0)
    print("===== Simulation results (raw) =====")
    print(plru_cache_l1.measurements)
    print(plru_cache_l2.measurements)


def run_LRU():
    l1_cache = Cache.Cache(size=l1size, associativity=l1assoc, inclusion_property=inc_pol,
                           replacement_policy=rep_pol, block_size=blocksize)
    if l2size:
        l2_cache = Cache.Cache(size=l2size, associativity=l2assoc, inclusion_property=inc_pol,
                               replacement_policy=rep_pol, block_size=blocksize)
    for inst in instruction_queue:
        status = l1_cache.execute(inst)
        if l2size:
            if l1_cache.is_write_back:
                l2_cache.execute(['w', l1_cache.write_back_inst])
            if status != 0:
                l2_cache.execute(['r', inst[1]])
    print("===== L1 contents =====")
    l1_cache.display_cache_content()
    if l2size:
        print("===== L2 contents =====")
        l2_cache.display_cache_content()
    l1_cache.getMissRate(1)
    l1_cache.getMemoryTraffic(1, 0)
    print("===== Simulation results (raw) =====")
    print(l1_cache.measurements)
    print(l2_cache.measurements)


def run_OPT():
    l1_cache = Cache.Cache(size=l1size, associativity=l1assoc, inclusion_property=inc_pol,
                           replacement_policy=rep_pol, block_size=blocksize)

    if l2size:
        l2_cache = Cache.Cache(size=l2size, associativity=l2assoc, inclusion_property=inc_pol,
                               replacement_policy=rep_pol, block_size=blocksize)

    generate_future_dict(l1_cache)
    for inst in instruction_queue:
        status = l1_cache.execute(inst)
        if l2size:
            if l1_cache.is_write_back:
                l2_cache.execute(['w', l1_cache.write_back_inst])
            if status != 0:
                l2_cache.execute(['r', inst[1]])
    print("===== L1 contents =====")
    l1_cache.display_cache_content()
    if l2size:
        print("===== L2 contents =====")
        l2_cache.display_cache_content()
    l1_cache.getMissRate(1)
    l1_cache.getMemoryTraffic(1, 0)
    print("===== Simulation results (raw) =====")
    print(l1_cache.measurements)
    print(l2_cache.measurements)


instruction_queue = []
blocksize, l1size, l1assoc, l2size, l2assoc, rep_pol, inc_pol, file = configurator()
read_tracefile(file)

if rep_pol == 0:
    print("=========== LRU ============")
    run_LRU()
elif rep_pol == 1:
    print("======== Pseudo LRU ========")
    run_PLRU()
else:
    print("=========== OPT ============")
    run_OPT()
