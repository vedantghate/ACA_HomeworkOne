import sys
import Cache


def configurator():
    """
    Parses the command and extracts the configuration parameters from it
    <BLOCKSIZE> <L1_SIZE> <L1_ASSOC> <L2_SIZE> <L2_ASSOC>
    <REPLACEMENT_POLICY> <INCLUSION_PROPERTY> <trace_file>
    0 for LRU, 1 for PLRU, 2 for Optimal.
    0 for non-inclusive, 1 for inclusive.
    :return: The configuration parameters
    """
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
    f = open(path, "r", encoding='utf-8')
    i = 0
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


def printResults(l1_obj, l2_obj):
    rp_codes = ['LRU', 'Pseudo-LRU', 'Optimal']
    ip_codes = ['non-inclusive', 'inclusive']
    print("===== Simulator configuration =====")
    print("BLOCKSIZE: ", blocksize)
    print("L1_SIZE: ", l1size)
    print("L1_ASSOC: ", l1assoc)
    print("L2_SIZE: ", l2size)
    print("L2_ASSOC: ", l2assoc)
    print("REPLACEMENT POLICY: ", rp_codes[rep_pol])
    print("INCLUSION PROPERTY: ", ip_codes[inc_pol])
    print("trace_file: ", file.split('/')[-1])
    print("===== L1 contents =====")
    l1_obj.display_cache_content()
    if l2size:
        print("===== L2 contents =====")
        l2_obj.display_cache_content()
    print("===== Simulation results (raw) =====")
    print("a. number of L1 reads: ", l1_obj.measurements['reads'])
    print("b. number of L1 read misses: ", l1_obj.measurements['reads_miss'])
    print("c. number of L1 writes: ", l1_obj.measurements['writes'])
    print("d. number of L1 write misses: ", l1_obj.measurements['writes_miss'])
    print("e. L1 miss rate: ", l1_obj.measurements['miss_rate'])
    print("f. number of L1 writebacks: ", l1_obj.measurements['num_writebacks'])
    print("g. number of L2 reads: ", l2_obj.measurements['reads'])
    print("h. number of L2 read misses: ", l2_obj.measurements['reads_miss'])
    print("i. number of L2 writes: ", l2_obj.measurements['writes'])
    print("j. number of L2 write misses: ", l2_obj.measurements['writes_miss'])
    print("k. L2 miss rate: ", l2_obj.measurements['miss_rate'])
    print("l. number of L2 writebacks: ", l2_obj.measurements['num_writebacks'])
    memory_traffic = l2_obj.measurements['memory_traffic'] if l2size else l1_obj.measurements['memory_traffic']
    print("m. total memory traffic: ", memory_traffic)


def run_PLRU():
    plru_cache_l1 = Cache.PLRUCache(size=l1size, associativity=l1assoc, inclusion_property=inc_pol,
                                    replacement_policy=rep_pol, block_size=blocksize, is_highest=True)

    plru_cache_l2 = Cache.PLRUCache(size=l2size, associativity=l2assoc, inclusion_property=inc_pol,
                                    replacement_policy=rep_pol, block_size=blocksize, is_highest=False)
    for inst in instruction_queue:
        status = plru_cache_l1.execute(inst)
        if l2size:
            if plru_cache_l1.is_write_back:
                plru_cache_l2.execute(['w', plru_cache_l1.write_back_inst])
            if status != 0:
                plru_cache_l2.execute(['r', inst[1]])

    plru_cache_l1.getMissRate(1)
    plru_cache_l2.getMissRate(2)
    plru_cache_l1.getMemoryTraffic(1, 0)
    plru_cache_l2.getMemoryTraffic(2, 0)

    printResults(plru_cache_l1, plru_cache_l2)


def run_LRU():
    l1_cache = Cache.Cache(size=l1size, associativity=l1assoc, inclusion_property=inc_pol,
                           replacement_policy=rep_pol, block_size=blocksize, is_highest=True)

    l2_cache = Cache.Cache(size=l2size, associativity=l2assoc, inclusion_property=inc_pol,
                           replacement_policy=rep_pol, block_size=blocksize, is_highest=False)

    for inst in instruction_queue:
        status = l1_cache.execute(inst)
        if l2size:
            if l1_cache.is_write_back:
                l2_cache.execute(['w', l1_cache.write_back_inst])
                if l2_cache.is_issue_invalidate:
                    l1_cache.invalidate_block(l2_cache.invalidate_inst)
                    l2_cache.clear_validation_flags()
            if status != 0:
                l2_cache.execute(['r', inst[1]])
                if l2_cache.is_issue_invalidate:
                    l1_cache.invalidate_block(l2_cache.invalidate_inst)
                    l2_cache.clear_validation_flags()

    l1_cache.getMissRate(1)
    l2_cache.getMissRate(2)
    l1_cache.getMemoryTraffic(1, 0)
    l2_cache.getMemoryTraffic(2, l1_cache.measurements['direct_writeback'])

    printResults(l1_cache, l2_cache)


def run_OPT():
    l1_cache = Cache.Cache(size=l1size, associativity=l1assoc, inclusion_property=inc_pol,
                           replacement_policy=rep_pol, block_size=blocksize, is_highest=True)

    l2_cache = Cache.Cache(size=l2size, associativity=l2assoc, inclusion_property=inc_pol,
                           replacement_policy=rep_pol, block_size=blocksize, is_highest=False)

    generate_future_dict(l1_cache)
    for inst in instruction_queue:
        status = l1_cache.execute(inst)
        if l2size:
            if l1_cache.is_write_back:
                l2_cache.execute(['w', l1_cache.write_back_inst])
            if status != 0:
                l2_cache.execute(['r', inst[1]])

    l1_cache.getMissRate(1)
    l2_cache.getMissRate(2)
    l1_cache.getMemoryTraffic(1, 0)
    l2_cache.getMemoryTraffic(2, 0)

    printResults(l1_cache, l2_cache)


def get_aat_and_area(htl1, htl2, al1, al2, l1, l2):
    aat = 0.0
    if l2size == 0:
        aat = htl1 + l1.measurements['miss_rate'] * 100
    else:
        aat = htl1 + l1.measurements['miss_rate']*(htl2 + l2.measurements['miss_rate']*100)
    area = al1 + al2
    return aat, area


# =========== Runner block ============

instruction_queue = []
blocksize, l1size, l1assoc, l2size, l2assoc, rep_pol, inc_pol, file = configurator()
read_tracefile(file)

if rep_pol == 0:
    run_LRU()
elif rep_pol == 1:
    run_PLRU()
else:
    run_OPT()

# ===================================
