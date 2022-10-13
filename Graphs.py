import math
import re
import subprocess

import numpy as np

L1_size = [2 ** x for x in range(10, 21)]
log_2_l1_size = [math.log2(2 ** x) for x in range(10, 21)]
assoc = [1, 2, 4, 8, "full"]
miss_rates = np.zeros((5, 11))
aat_l1 = np.zeros((5, 11))

hit_times_32 = [
    [0.114797, 0.140329, 0.14682, 0.14682, 0.155484],  # 10
    [0.12909, 0.161691, 0.154496, 0.180686, 0.176515],  # 11
    [0.147005, 0.181131, 0.185685, 0.189065, 0.182948],  # 12
    [0.16383, 0.194195, 0.211173, 0.212911, 0.198581],  # 13
    [0.16383, 0.194195, 0.211173, 0.212911, 0.198581],  # 14
    [0.198417, 0.223917, 0.233936, 0.254354, 0.205608],  # 15
    [0.233353, 0.262446, 0.27125, 0.288511, 0.22474],  # 16
    [0.294627, 0.300727, 0.319481, 0.341213, 0.276281],  # 17
    [0.3668, 0.374603, 0.38028, 0.401236, 0.322486],  # 18
    [0.443812, 0.445929, 0.457685, 0.458925, 0.396009],  # 19
    [0.563451, 0.567744, 0.564418, 0.578177, 0.475728],  # 20
    [0.69938, 0.706046, 0.699607, 0.705819, 0.588474]  # 21
]

for x in range(len(assoc)):
    for y in range(len(L1_size)):
        if assoc[x] == "full":
            command = "python main.py 32 {} {} 0 0 0 0 ../traces/gcc_trace.txt".format(L1_size[y], int(L1_size[y] / 32))
        else:
            command = "python main.py 32 {} {} 0 0 0 0 ../traces/gcc_trace.txt".format(L1_size[y], assoc[x])
        output = subprocess.check_output(command, shell=True)
        output = output.decode("utf-8")
        val = re.findall("L1 miss rate:\\s+(\\d.\\d+)+", output)[0]
        miss_rates[x][y] = val
        aat_l1[x][y] = float(val) * 100 + hit_times_32[y][x]
        print("Size: " + str(L1_size[y]) + " Assoc: " + str(assoc[x]) + " L1 Miss Rate: " + str(val) + " AAT: " + str(
            aat_l1[x][y]))
    print("\n")

import pandas as pd

print("\n\nTable 1:")
print(pd.DataFrame(miss_rates, columns=log_2_l1_size, index=assoc))
print("\n\nTable 2:")
print(pd.DataFrame(aat_l1, columns=log_2_l1_size, index=[assoc]))

import matplotlib.pyplot as plt

# Graph 1 - log2(size) vs Miss rate
for x in range(len(assoc)):
    plt.xlabel("log2(SIZE) bytes")
    plt.ylabel("L1 Mis Rates")
    plt.xticks(log_2_l1_size)
    plt.yticks(miss_rates[x])
    plt.plot(log_2_l1_size, miss_rates[x], label="Assoc " + str(assoc[x]))
plt.legend()
plt.savefig('/Users/jarvis/MS CS/Spring 22/ACA/AssignmentOne/Homework-I/graphs/Graph1.png')
plt.close()

# Graph 2 - log2(size) vs Average Access Time
for x in range(len(assoc)):
    plt.xlabel("log2(SIZE) bytes")
    plt.ylabel("L1 AAT(Average Access time)")
    plt.xticks(log_2_l1_size)
    plt.yticks(aat_l1[:][x])
    plt.plot(log_2_l1_size, aat_l1[:][x], label="Assoc " + str(assoc[x]))
plt.legend()
plt.savefig('/Users/jarvis/MS CS/Spring 22/ACA/AssignmentOne/Homework-I/graphs/Graph2.png')
plt.close()

# Graph 3 - log2(size) vs Average Access Time
L1_size = [2 ** x for x in range(10, 19)]
log_2_l1_size = [math.log2(2 ** x) for x in range(10, 19)]
miss_rates = np.zeros((3, 9))
aat_l1 = np.zeros((3, 9))
rep_pol = [0, 1, 2]
assoc = 4

hit_times_32_assoc_4 = [
    [0.14682],  # 10
    [0.154496],  # 11
    [0.185685],  # 12
    [0.211173],  # 13
    [0.211173],  # 14
    [0.233936],  # 15
    [0.27125],  # 16
    [0.319481],  # 17
    [0.38028],  # 18
    [0.457685],  # 19
    [0.564418],  # 20
    [0.699607]  # 21
]

for x in range(len(rep_pol)):
    for y in range(len(L1_size)):
        command = "python main.py 32 {} 4 0 0 {} 0 ../traces/gcc_trace.txt".format(L1_size[y], rep_pol[x])
        output = subprocess.check_output(command, shell=True)
        output = output.decode("utf-8")
        val = re.findall("L1 miss rate:\\s+(\\d.\\d+)+", output)[0]
        miss_rates[x][y] = val
        aat_l1[x][y] = float(val) * 100 + hit_times_32_assoc_4[y][0]
        print("Size: " + str(L1_size[y]) + " Assoc: " + str(assoc) + " L1 Miss Rate: " + str(val) + " AAT: " + str(
            aat_l1[x][y]))
    print("\n")
rp = ["LRU", "Pseudo LRU", "OPT"]
print("\n\nTable 3:")
print(pd.DataFrame(aat_l1, columns=log_2_l1_size, index=rp))

for x in range(len(rep_pol)):
    plt.xlabel("log2(SIZE) bytes")
    plt.ylabel("L1 AAT(Average Access time)")
    plt.xticks(log_2_l1_size)
    plt.yticks(aat_l1[:][x])
    plt.plot(log_2_l1_size, aat_l1[:][x], label="RP " + rp[x])
plt.legend()
plt.savefig('/Users/jarvis/MS CS/Spring 22/ACA/AssignmentOne/Homework-I/graphs/Graph3.png')
plt.close()

# Graph 4 - log2(size) vs Average Access Time
L2_size = [2 ** x for x in range(11, 17)]
log_2_l2_size = [math.log2(2 ** x) for x in range(11, 17)]
aat_l2 = np.zeros((2, 6))
inc_pol = [0, 1]

hit_times_32_assoc_8 = [
    [0.14682],  # 10
    [0.180686],  # 11
    [0.189065],  # 12
    [0.212911],  # 13
    [0.212911],  # 14
    [0.254354],  # 15
    [0.288511],  # 16
    [0.341213],  # 17
    [0.401236],  # 18
    [0.458925],  # 19
    [0.578177],  # 20
    [0.705819]  # 21
]
for x in range(len(inc_pol)):
    for y in range(len(L2_size)):
        command = "python main.py 32 1024 4 {} 8 0 {} ../traces/gcc_trace.txt".format(L2_size[y], inc_pol[x])
        output = subprocess.check_output(command, shell=True)
        output = output.decode("utf-8")
        l1_mr = re.findall("L1 miss rate:\\s+(\\d.\\d+)+", output)[0]
        l2_mr = re.findall("L2 miss rate:\\s+(\\d.\\d+)+", output)[0]
        aat_l2[x][y] = 0.14682 + float(l1_mr) * (hit_times_32_assoc_8[y][0] + float(l2_mr) * 100)
        print("Size: " + str(L2_size[y]) + " L1 Miss Rate: " + l1_mr + " L2 Miss Rate: " + l2_mr + " AAT: " + str(
            aat_l2[x][y]))
    print("\n")
ip = ["non-inclusive", "inclusive"]
print("\n\nTable 4:")
print(pd.DataFrame(aat_l2, columns=log_2_l2_size, index=ip))

for x in range(len(inc_pol)):
    plt.xlabel("log2(SIZE) bytes")
    plt.ylabel("L1 AAT(Average Access time)")
    plt.xticks(log_2_l2_size)
    plt.yticks(aat_l2[:][x])
    plt.plot(log_2_l2_size, aat_l2[:][x], label="IP " + ip[x])
plt.legend()
plt.savefig('/Users/jarvis/MS CS/Spring 22/ACA/AssignmentOne/Homework-I/graphs/Graph4.png')
plt.close()