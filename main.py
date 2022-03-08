import Cache

instruction_queue = []


def read_tracefile():
    f = open("/Users/jarvis/MS CS/Spring 22/ACA/AssignmentOne/Traces/vortex_trace.txt", "r")
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


l1_cache = Cache.Cache(size=256, associativity=1, inclusion_property=0, replacement_policy=1, block_size=32)
read_tracefile()
generate_future_dict(l1_cache)
for inst in instruction_queue:
    l1_cache.execute(inst)
'''
# generate_future_dict(l1_cache)

l1_cache.execute(['w', 'FF0040E0'])
l1_cache.display_cache_content()

l1_cache.execute(['w', 'BEEF005C'])
l1_cache.display_cache_content()

l1_cache.execute(['w', 'FF0040E2'])
l1_cache.display_cache_content()

l1_cache.execute(['w', 'FF0040E8'])
l1_cache.display_cache_content()

l1_cache.execute(['w', '00101078'])
l1_cache.display_cache_content()

l1_cache.execute(['w', '002183E0'])
'''

l1_cache.display_cache_content()
l1_cache.getMissRate(1)
l1_cache.getMemoryTraffic(1, 0)
print(l1_cache.measurements)
