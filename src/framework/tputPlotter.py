#!/usr/bin/env python
#Author: Kashyap Thimmaraju
#Email: kashyap.thimmaraju@sec.t-labs-tu-berlin.de
'''
Parse the tput cvs and plot as barcharts for comparison
'''
import re
import json
import pprint
import matplotlib.pyplot as plt
import numpy as np
import os.path
import csv

# data variables
dataPath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-submission/throughput/"
dataPath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/throughput/"
dataFile = "trajectoryThroughput.json"
detectors = ['1', '2', '4', '6', '8']
sharedTput = "sharedCPU/tputShared.csv"
isolatedTput = "isolatedCPU/tputIsolated.csv"
# results variables
resultsPath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-submission/throughput/plots/"
resultsFile = "tput.png"
sharedResultFile = "tputShared.pdf"
isolatedResultFile = "tputIsolated.pdf"
# matplotlib variables
lineStyles = ['dotted', 'dotted', 'dotted', 'dashed', 'dashed']
# lineColours = ['#0000CD', '#097054', '#6599FF', '#5B7444']
lineColours = ['#405774', '#CD6607', '#6787B0', '#F6A03D'] #Blues for gcc, Oranges for clang
# lineStyles = ['', '', '', '', '']
markerStyles = ['1', '2', '3', '4', 'D']
#markerStyles = ['D', 's', 'o', '^', 'D']
fontsize = 8
labels = [u'1', u'2', u'4', u'6', u'8']

# DATA
# 1   793     863     1013
# 2   1022    1156    1701
# 4   1095    1363    1865
# 6   1110    1458    2898
# 8   1347    1674    2921

def plotThroughput(baseline, oneOvs, twoOvs, fourOvs):
    print "plotCoreBasedThroughput"
    core1 =(793, 1022, 1095, 1110, 1347)
    core2 = (863, 1156, 1363, 1458, 1674)
    hyper = (1013, 1701, 1865, 2898, 2921)
    bShared = tuple(baseline["shared"])
    bIsolated = tuple(baseline["isolated"])
    bDpdk = tuple(baseline["dpdk"])

    fourbIsolated = tuple(fourbaseline["isolated"])
    fourbDpdk = tuple(fourbaseline["dpdk"])
    oneShared = tuple(oneOvs["shared"])
    oneIsolated = tuple(oneOvs["isolated"])
    oneDpdk = tuple(oneOvs["dpdk"])
    twoShared = tuple(twoOvs["shared"])
    twoIsolated = tuple(twoOvs["isolated"])
    twoDpdk = tuple(twoOvs["dpdk"])
    fourShared = tuple(fourOvs["shared"])
    fourIsolated = tuple(fourOvs["isolated"])
    fourDpdk = tuple(fourOvs["dpdk"])

    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5']
    colors = [u'#66c2a5', u'#fa8e63', u'#8da0cb', '#3D9970']
    fig = plt.figure(1, figsize = (6.974, 2.15512978986403),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 3, 1)
    plt.tight_layout()
    width = .25
    N = 3
    ind = np.arange(N)
    ax.yaxis.grid(True, linestyle='-.', which='major')
    rects1 = ax.bar(ind, bShared, width=width, color=colors[0], edgecolor='black')
    rects2 = ax.bar(ind + width, oneShared, width=width, color=colors[1], edgecolor='black')
    rects3 = ax.bar(ind + 2*width, twoShared, width=width, color=colors[2], edgecolor='black')
    rects3 = ax.bar(ind + 3*width, fourShared, width=width, color=colors[3], edgecolor='black')

    # ax.set_ylabel('Trajectories/s')
    # ax.set_yscale('log')
    plt.ylim((0, 1))
    ax.set_ylabel('Rx Tput (Mpps)')
    # ax.set_xlabel('Thread count')
    ax.set_xlabel('Shared Core (No Dpdk)')
    ax.set_xticks(ind + width + .15)
    ax.set_xticklabels(('p2p', 'p2v', 'v2v'))
    ax.set_axisbelow(True)
    # ax.set_xticklabels(('1', '2', '4', '6', '8'), fontsize=fontsize)
    # ax.set_yticklabels((0, 500, 1000, 1500, 2000, 2500, 3000),fontsize=fontsize)
    # ax.legend((rects1[0], rects2[0], rects3[0]), ('1 Core', '2 Core', 'Hyper-Threading'))

    box = ax.get_position()
    ax.set_position([box.x0 + box.width * .12, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])

    ax.annotate('Baseline', xy=(-0.1, 0.84), xycoords='data',
                xytext=(1.2, 0.88), arrowprops=dict(arrowstyle="->"))
    ax.annotate('1 Ovs', xy=(1.3, 0.380), xycoords='data',
                xytext=(1.2, 0.71), arrowprops=dict(arrowstyle="->"))
    ax.annotate('2 Ovs', xy=(1.5, 0.40), xycoords='data',
                xytext=(1.7, 0.6), arrowprops=dict(arrowstyle="->"))
    ax.annotate('4 Ovs', xy=(1.8, 0.42), xycoords='data',
                xytext=(2.225, 0.45), arrowprops=dict(arrowstyle="->"))

    ### Second plot with isolated cores
    ax = plt.subplot(1, 3, 2)
    width = .25
    N = 6
    ind = np.arange(N)
    ax.yaxis.grid(True, linestyle='-.', which='major')
    rects1 = ax.bar(ind, bIsolated, width=width, color=colors[0], edgecolor='black')
    rects2 = ax.bar(ind + width, twobIsolated, width=width, color=colors[1], edgecolor='black')
    rects3 = ax.bar(ind + 2*width, fourbIsolated, width=width, color=colors[2], edgecolor='black')

    rects4 = ax.bar(ind + 4*width, oneIsolated, width=width, color=colors[0], edgecolor='black')
    rects5 = ax.bar(ind + 5*width, twoIsolated, width=width, color=colors[1], edgecolor='black')
    rects6 = ax.bar(ind + 6*width, fourIsolated, width=width, color=colors[2], edgecolor='black')

    # ax.set_ylabel('Trajectories/s')
    # ax.set_yscale('log')
    # ax.set_ylabel('Rx Tput (Mpps)')
    # ax.set_xlabel('Thread count')
    plt.ylim((0, 5))
    ax.set_xlabel('Isolated Core (No Dpdk)')
    ax.set_xticks(ind + width + .15)
    ax.set_xticklabels(('p2p', 'p2v', 'v2v'))
    ax.set_axisbelow(True)
    box = ax.get_position()
    ax.set_position([box.x0 + box.width * .046, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])


    ### Third plot with dpdk
    ax = plt.subplot(1, 3, 3)
    width = .25
    N = 6
    ind = np.arange(N)
    ax.yaxis.grid(True, linestyle='-.', which='major')
    rects1 = ax.bar(ind, bDpdk, width=width, color=colors[0], edgecolor='black')
    rects2 = ax.bar(ind + width, twobDpdk, width=width, color=colors[1], edgecolor='black')
    rects3 = ax.bar(ind + 2*width, fourbDpdk, width=width, color=colors[2], edgecolor='black')

    rects4 = ax.bar(ind + 4*width, oneDpdk, width=width, color=colors[0], edgecolor='black')
    rects5 = ax.bar(ind + 5*width, twoDpdk, width=width, color=colors[1], edgecolor='black')
    rects6 = ax.bar(ind + 6*width, fourDpdk, width=width, color=colors[2], edgecolor='black')

    # ax.set_ylabel('Trajectories/s')
    # ax.set_yscale('log')
    # ax.set_ylabel('Rx Tput (Mpps)')
    # ax.set_xlabel('Thread count')
    plt.ylim((0, 15))
    ax.set_xlabel('Isolated Core (Dpdk)')
    ax.set_xticks(ind + width + .15)
    ax.set_xticklabels(('p2p', 'p2v', 'v2v'))
    ax.set_axisbelow(True)
    box = ax.get_position()
    ax.set_position([box.x0 + box.width * .046, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])


    # plt.show()
    # plt.close()
    plt.savefig(resultsPath + resultsFile)

def getData():
    print "getData"
    reader = csv.reader(open(dataPath+sharedTput, 'r'))
    d = {}
    phy2phy = {"phy2phy": []}
    phy2vm = {"phy2vm": []}
    vm2vm = {"vm2vm": []}
    for row in reader:
        if row[0] == "phy2phy":
            phy2phy["phy2phy"].append(row[1:])
        elif row[0] == "phy2vm2vm2phy":
            phy2vm["phy2vm"].append(row[1:])
        elif row[0] == "vm2vm":
            vm2vm["vm2vm"].append(row[1:])
        # d[row[0]].append(row[1:])
    pprint.pprint(phy2phy)
    pprint.pprint(phy2vm)
    pprint.pprint(vm2vm)
    d["phy2phy"] = phy2phy["phy2phy"]
    d["phy2vm"] = phy2vm["phy2vm"]
    d["vm2vm"] = vm2vm["vm2vm"]

    baseline = {"shared": [], "isolated": [], "dpdk": []}
    oneOvs = {"shared": [], "isolated": [], "dpdk": []}
    twoOvs = {"shared": [], "isolated": [], "dpdk": []}
    fourOvs = {"shared": [], "isolated": [], "dpdk": []}
    twobaseline = {"shared": [], "isolated": [], "dpdk": []}
    fourbaseline = {"shared": [], "isolated": [], "dpdk": []}

    keys = ["phy2phy", "phy2vm", "vm2vm"]
    for topo in keys:
        for t in d[topo]:
            if t[1] == "False":
                if t[0] == "Baseline_NoDPDK":
                    baseline["shared"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_OneOvs":
                    oneOvs["shared"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_TwoOvs":
                    twoOvs["shared"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_FourOvs":
                    fourOvs["shared"].append(float(t[3]))
            elif t[1] == "True":
                if t[0] == "Baseline_NoDPDK":
                    baseline["isolated"].append(float(t[3]))
                elif t[0] == "Baseline_NoDPDK_2Core":
                    twobaseline["isolated"].append(float(t[3]))
                elif t[0] == "Baseline_NoDPDK_4Core":
                    fourbaseline["isolated"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_OneOvs":
                    oneOvs["isolated"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_TwoOvs":
                    twoOvs["isolated"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_FourOvs":
                    fourOvs["isolated"].append(float(t[3]))
                elif t[0] == "Baseline_DPDK":
                    baseline["dpdk"].append(float(t[3]))
                elif t[0] == "Baseline_DPDK_2Core":
                    twobaseline["dpdk"].append(float(t[3]))
                elif t[0] == "Baseline_DPDK_4Core":
                    fourbaseline["dpdk"].append(float(t[3]))
                elif t[0] == "SRIOV_DPDK_OneOvs":
                    oneOvs["dpdk"].append(float(t[3]))
                elif t[0] == "SRIOV_DPDK_TwoOvs":
                    twoOvs["dpdk"].append(float(t[3]))
                elif t[0] == "SRIOV_DPDK_FourOvs":
                    fourOvs["dpdk"].append(float(t[3]))
    pprint.pprint(baseline)
    pprint.pprint(oneOvs)
    pprint.pprint(twoOvs)
    pprint.pprint(fourOvs)
    pprint.pprint(twobaseline)
    pprint.pprint(fourbaseline)

    reader = csv.reader(open(dataPath+isolatedTput, 'r'))
    d = {}
    phy2phy = {"phy2phy": []}
    phy2vm = {"phy2vm": []}
    vm2vm = {"vm2vm": []}
    for row in reader:
        if row[0] == "phy2phy":
            phy2phy["phy2phy"].append(row[1:])
        elif row[0] == "phy2vm2vm2phy":
            phy2vm["phy2vm"].append(row[1:])
        elif row[0] == "vm2vm":
            vm2vm["vm2vm"].append(row[1:])
        # d[row[0]].append(row[1:])
    pprint.pprint(phy2phy)
    pprint.pprint(phy2vm)
    pprint.pprint(vm2vm)
    d["phy2phy"] = phy2phy["phy2phy"]
    d["phy2vm"] = phy2vm["phy2vm"]
    d["vm2vm"] = vm2vm["vm2vm"]

    baseline["isolated"] = baseline["shared"]
    oneOvs["isolated"] = oneOvs["shared"]
    # twoOvs = {"shared": [], "isolated": []}
    # fourOvs = {"shared": [], "isolated": []}

    # pprint.pprint(d)
    keys = ["phy2phy", "phy2vm", "vm2vm"]
    for topo in keys:
        for t in d[topo]:
            if t[1] == "False":
                if t[0] == "Baseline_NoDPDK":
                    baseline["shared"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_OneOvs":
                    oneOvs["shared"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_TwoOvs":
                    twoOvs["shared"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_FourOvs":
                    fourOvs["shared"].append(float(t[3]))
            elif t[1] == "True":
                if t[0] == "Baseline_NoDPDK":
                    baseline["isolated"].append(float(t[3]))
                elif t[0] == "Baseline_NoDPDK_2Core":
                    twobaseline["isolated"].append(float(t[3]))
                elif t[0] == "Baseline_NoDPDK_4Core":
                    fourbaseline["isolated"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_OneOvs":
                    oneOvs["isolated"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_TwoOvs":
                    twoOvs["isolated"].append(float(t[3]))
                elif t[0] == "SRIOV_NoDPDK_FourOvs":
                    fourOvs["isolated"].append(float(t[3]))
                elif t[0] == "Baseline_DPDK":
                    baseline["dpdk"].append(float(t[3]))
                elif t[0] == "Baseline_DPDK_2Core":
                    twobaseline["dpdk"].append(float(t[3]))
                elif t[0] == "Baseline_DPDK_4Core":
                    fourbaseline["dpdk"].append(float(t[3]))
                elif t[0] == "SRIOV_DPDK_OneOvs":
                    oneOvs["dpdk"].append(float(t[3]))
                elif t[0] == "SRIOV_DPDK_TwoOvs":
                    twoOvs["dpdk"].append(float(t[3]))
                elif t[0] == "SRIOV_DPDK_FourOvs":
                    fourOvs["dpdk"].append(float(t[3]))
            # pprint.pprint(baseline)
    for k in fourOvs.keys():
        fourOvs[k].append(float(0.0))
    # baseline["dpdk"] = [0.0, 0.0, 0.0]
    pprint.pprint(baseline)
    pprint.pprint(oneOvs)
    pprint.pprint(twoOvs)
    pprint.pprint(fourOvs)
    pprint.pprint(twobaseline)
    pprint.pprint(fourbaseline)
    return baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline


if __name__ == "__main__":
    baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline = getData()
    plotThroughput(baseline, oneOvs, twoOvs, fourOvs)