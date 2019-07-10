#!/usr/bin/env python
#Author: Kashyap Thimmaraju
#Email: kashyap.thimmaraju@sect-tu-berlin.de
'''
Plot the resources, throughput and latency for the shared model
'''
import re
import json
import pprint
from visualizer import read_lat_dict
import src.framework.tputPlotter as tPlotter
import matplotlib.pyplot as plt
import numpy as np
import os.path
import csv
from src.framework.BenchPloter import *

figurePath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/plots/bench/"
csvPath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/benchmarks/"

fIperfBenchmark = csvPath + "Parsed_Iperf_Benchmark_Data.csv"
fAbBenchmark = csvPath + "Parsed_Ab_Benchmark_Data.csv"
fMemBenchmark = csvPath + "Parsed_Mem_Benchmark_Data.csv"
keys = ["MEAN", "STD"]

def plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=1, baselineTwo="", baselineFour=""):
    print "plotIperf()"
    print "plotThroughput"
    # if pltN == 1 or pltN == 3:
    #     baselineTwo["MEAN"] = (float("{0:.2f}".format(baselineTwo["MEAN"][0]/1000.0)),
    #                            float("{0:.2f}".format(baselineTwo["MEAN"][1]/1000.0)))
    #     baselineFour["MEAN"] = (float("{0:.2f}".format(baselineFour["MEAN"][0]/1000.0)),
    #                            float("{0:.2f}".format(baselineFour["MEAN"][1]/1000.0)))

    b, one, two, four, btwo, bfour = baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour

    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5']
    colors = [u'#66c2a5', u'#fa8e63', u'#8da0cb', '#3D9970']
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5' ]
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5', '#7D7D7D', '#B1B1B1' ]
    if pltN == 1:
        fig = plt.figure(1, figsize = (6.974, 2.15512978986403/1),frameon=True)
        fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 5, pltN)
    plt.tight_layout()
    width = .1
    N = 2
    ind = np.arange(N)
    # ind = (0, 2)
    ax.yaxis.grid(True, linestyle='-.', which='major')
    # rects1 = ax.bar(ind, b["MEAN"], width=width, color=colors[0], edgecolor='black')
    # rects2 = ax.bar(ind + width, one["MEAN"], width=width, color=colors[1], edgecolor='black')
    # rects3 = ax.bar(ind + 2*width, two["MEAN"], width=width, color=colors[2], edgecolor='black')
    # rects4 = ax.bar(ind + 3*width, four["MEAN"], width=width, color=colors[3], edgecolor='black')
    if resourceType == "shared":
        rects1 = ax.bar(ind, b["MEAN"], yerr=b["STD"], width=width, color=colors[0], edgecolor='none')
        rects2 = ax.bar(ind + width, one["MEAN"], yerr=one["STD"], width=width, color=colors[1], edgecolor='none')
        rects3 = ax.bar(ind + 2 * width, two["MEAN"], yerr=two["STD"], width=width, color=colors[2], edgecolor='none')
        rects4 = ax.bar(ind + 3 * width, four["MEAN"], yerr=four["STD"], width=width, color=colors[3], edgecolor='none')
    elif resourceType == "isolated" or resourceType == "dpdk":
        rects1 = ax.bar(ind, b["MEAN"], yerr=b["STD"], width=width, color=colors[0], edgecolor='none', label='_nolegend_')
        rects2 = ax.bar(ind + width, btwo["MEAN"], yerr=btwo["STD"], width=width, color=colors[4], edgecolor='none', label="Baseline\n2 cores")
        rects3 = ax.bar(ind + 2 * width, bfour["MEAN"], yerr=bfour["STD"], width=width, color=colors[5], edgecolor='none',
                        label='Baseline\n4 cores')
        rects4 = ax.bar(ind + 4 * width, one["MEAN"], yerr=one["STD"], width=width, color=colors[1], edgecolor='none', label='_nolegend_')
        rects5 = ax.bar(ind + 5 * width, two["MEAN"], yerr=two["STD"], width=width, color=colors[2], edgecolor='none', label='_nolegend_')
        rects6 = ax.bar(ind + 6 * width, four["MEAN"], yerr=four["STD"], width=width, color=colors[3], edgecolor='none', label='_nolegend_')

    if pltN == 1:
        app = resourceType + '\nIperf '
        ylabel = app + '(Gbps)'
        plt.ylim((0, 10))
        if resourceType == "shared":
            plt.xlabel("(a)")
        elif resourceType == "isolated":
            plt.xlabel("(f)")
        elif resourceType == "dpdk":
            plt.xlabel("(k)")
        # ax.annotate('Shared', xy=(0., 0.5), xycoords=ax.yaxis.label,
        #             xytext=(1.2, 0.88), ha='right', va='center')
    elif pltN == 2:
        app = 'Apch '
        ylabel = app + '(KReqs/s)'
        plt.ylim((0, 25))
        if resourceType == "shared":
            plt.xlabel("(b)")
        elif resourceType == "isolated":
            plt.xlabel("(g)")
        elif resourceType == "dpdk":
            plt.xlabel("(l)")
    elif pltN == 3:
        app = 'Mchd '
        ylabel = app + '(KOps/s)'
        plt.ylim((0, 310))
        if resourceType == "shared":
            plt.xlabel("(c)")
        elif resourceType == "isolated":
            plt.xlabel("(h)")
        elif resourceType == "dpdk":
            plt.xlabel("(m)")
    ax.set_ylabel(ylabel)    # ax.set_xlabel('Shared Core (No Dpdk)')
    ax.set_xticks(ind + width + .15)
    ax.set_xticklabels(('B MTS\np2v', '   B MTS\nv2v'), fontsize=6)
    ax.set_axisbelow(True)

    # box = ax.get_position()
    # ax.set_position([box.x0 + box.width * .12, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])
    # plt.show()
    # plt.close()
    plt.savefig(figurePath + figureName)

def plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=4, baselineTwo="", baselineFour=""):
    print "plotIperf()"
    print "plotThroughput"
    # if pltN == 6:
    #     baselineTwo["MEAN"] = (float("{0:.2f}".format(baselineTwo["MEAN"][0]/1000.0)),
    #                            float("{0:.2f}".format(baselineTwo["MEAN"][1]/1000.0)))
    #     baselineFour["MEAN"] = (float("{0:.2f}".format(baselineFour["MEAN"][0]/1000.0)),
    #                            float("{0:.2f}".format(baselineFour["MEAN"][1]/1000.0)))

    b, one, two, four, btwo, bfour = baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour

    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5']
    colors = [u'#66c2a5', u'#fa8e63', u'#8da0cb', '#3D9970']
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5' ]
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5', '#7D7D7D', '#B1B1B1' ]
    if pltN == 1:
        fig = plt.figure(1, figsize = (6.974, 2.15512978986403/1),frameon=True)
        fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 5, pltN)
    plt.tight_layout()
    width = .1
    N = 2
    ind = np.arange(N)
    # ind = (0, 2)
    ax.yaxis.grid(True, linestyle='-.', which='major')
    if resourceType == "shared":
        rects1 = ax.bar(ind, b["MEAN"], yerr=b["STD"], width=width, color=colors[0], edgecolor='none')
        rects2 = ax.bar(ind + width, one["MEAN"], yerr=one["STD"], width=width, color=colors[1], edgecolor='none')
        rects3 = ax.bar(ind + 2*width, two["MEAN"], yerr=two["STD"], width=width, color=colors[2], edgecolor='none')
        rects4 = ax.bar(ind + 3*width, four["MEAN"], yerr=four["STD"], width=width, color=colors[3], edgecolor='none')
    elif resourceType == "isolated" or resourceType == "dpdk":
        rects1 = ax.bar(ind, b["MEAN"], yerr=b["STD"], width=width, color=colors[0], edgecolor='none', label='_nolegend_')
        rects2 = ax.bar(ind + width, btwo["MEAN"], yerr=btwo["STD"], width=width, color=colors[4], edgecolor='none', label="Baseline\n2 cores")
        rects3 = ax.bar(ind + 2 * width, bfour["MEAN"], yerr=bfour["STD"], width=width, color=colors[5], edgecolor='none',
                        label='Baseline\n4 cores')
        rects4 = ax.bar(ind + 4 * width, one["MEAN"], yerr=one["STD"], width=width, color=colors[1], edgecolor='none', label='_nolegend_')
        rects5 = ax.bar(ind + 5 * width, two["MEAN"], yerr=two["STD"], width=width, color=colors[2], edgecolor='none', label='_nolegend_')
        rects6 = ax.bar(ind + 6 * width, four["MEAN"], yerr=four["STD"], width=width, color=colors[3], edgecolor='none', label='_nolegend_')


    # if resourceType == "shared":
    #     plt.ylim((0, 1))
    # elif resourceType == "isolated":
    #     plt.ylim((0, 5))
    # elif resourceType == "dpdk":
    #     plt.ylim((0, 15))
    if pltN == 4:
        app = 'Apch '
        plt.ylim((0, 300))
        if resourceType == "shared":
            plt.xlabel("(d)")
        elif resourceType == "isolated":
            plt.xlabel("(i)")
        elif resourceType == "dpdk":
            plt.xlabel("(n)")
    elif pltN == 5:
        app = 'Mchd '
        plt.ylim((0, 25))
        if resourceType == "shared":
            plt.xlabel("(e)")
        elif resourceType == "isolated":
            plt.xlabel("(j)")
        elif resourceType == "dpdk":
            plt.xlabel("(o)")
    ylabel = app + 'resp. time (ms)'
    ax.set_ylabel(ylabel)
    # ax.set_xlabel('Shared Core (No Dpdk)')
    ax.set_xticks(ind + width + .15)
    ax.set_xticklabels(('  B MTS\np2v', '   B MTS\nv2v'), fontsize=6)
    ax.set_axisbelow(True)

    # box = ax.get_position()
    # ax.set_position([box.x0 + box.width * .12, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])
    # plt.show()
    # plt.close()
    plt.savefig(figurePath + figureName)

def reorderDict(data, resourceType="shared"):
    print "reorderDict()"
    '''
    Structure of data['*'][0-11]
    [0] Baseline p2v
    [1] SRIOV_OneOvs p2v
    [2] SRIOV_TwoOvs p2v
    [3] SRIOV_FourOvs p2v
    [4] Baseline v2v
    [5] SRIOV_OneOvs v2v
    [6] SRIOV_TwoOvs v2v
    [7] SRIOV_FourOvs v2v
    [8] Baseline_NoDPDK_2Core p2v
    [9] Baseline_NoDPDK_4Core p2v
    [10] Baseline_NoDPDK_2Core v2v
    [11] Baseline_NoDPDK_4Core v2v
    [12] Baseline_DPDK_2Core p2v
    [13] Baseline_DPDK_4Core p2v
    [14] Baseline_DPDK_2Core v2v
    [15] Baseline_DPDK_4Core v2v
    '''
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = \
        {"MEAN": (), "STD": ()},\
        {"MEAN": (), "STD": ()},\
        {"MEAN": (), "STD": ()},\
        {"MEAN": (), "STD": ()},\
        {"MEAN": (), "STD": ()},\
        {"MEAN": (), "STD": ()}
    if resourceType == "shared":
        baseline["MEAN"] = data['cpuShared_without_DPDK_MEAN'][0], data['cpuShared_without_DPDK_MEAN'][4]
        oneOvs["MEAN"] = data['cpuShared_without_DPDK_MEAN'][1], data['cpuShared_without_DPDK_MEAN'][5]
        twoOvs["MEAN"] = data['cpuShared_without_DPDK_MEAN'][2], data['cpuShared_without_DPDK_MEAN'][6]
        fourOvs["MEAN"] = data['cpuShared_without_DPDK_MEAN'][3], 0
        baseline["STD"] = data['cpuShared_without_DPDK_STD'][0]*2, data['cpuShared_without_DPDK_STD'][4]*2
        oneOvs["STD"] = data['cpuShared_without_DPDK_STD'][1]*2, data['cpuShared_without_DPDK_STD'][5]*2
        twoOvs["STD"] = data['cpuShared_without_DPDK_STD'][2]*2, data['cpuShared_without_DPDK_STD'][6]*2
        fourOvs["STD"] = data['cpuShared_without_DPDK_STD'][3]*2, 0
    elif resourceType == "isolated":
        baseline["MEAN"] = data['cpuIsolation_without_DPDK_MEAN'][0], data['cpuIsolation_without_DPDK_MEAN'][4]
        oneOvs["MEAN"] = data['cpuIsolation_without_DPDK_MEAN'][1], data['cpuIsolation_without_DPDK_MEAN'][5]
        twoOvs["MEAN"] = data['cpuIsolation_without_DPDK_MEAN'][2], data['cpuIsolation_without_DPDK_MEAN'][6]
        fourOvs["MEAN"] = data['cpuIsolation_without_DPDK_MEAN'][3], 0
        baseline["STD"] = data['cpuIsolation_without_DPDK_STD'][0]*2, data['cpuIsolation_without_DPDK_STD'][4]*2
        oneOvs["STD"] = data['cpuIsolation_without_DPDK_STD'][1]*2, data['cpuIsolation_without_DPDK_STD'][5]*2
        twoOvs["STD"] = data['cpuIsolation_without_DPDK_STD'][2]*2, data['cpuIsolation_without_DPDK_STD'][6]*2
        fourOvs["STD"] = data['cpuIsolation_without_DPDK_STD'][3]*2, 0
        baselineTwo["MEAN"] = data['cpuIsolation_without_DPDK_MEAN'][7], data['cpuIsolation_without_DPDK_MEAN'][9]
        baselineFour["MEAN"] = data['cpuIsolation_without_DPDK_MEAN'][8], data['cpuIsolation_without_DPDK_MEAN'][10]
        baselineTwo["STD"] = data['cpuIsolation_without_DPDK_STD'][7]*2, data['cpuIsolation_without_DPDK_STD'][9]*2
        baselineFour["STD"] = data['cpuIsolation_without_DPDK_STD'][8]*2, data['cpuIsolation_without_DPDK_STD'][10]*2
    elif resourceType == "dpdk":
        baseline["MEAN"] = data['cpuIsolation_with_DPDK_MEAN'][0], data['cpuIsolation_with_DPDK_MEAN'][4]
        oneOvs["MEAN"] = data['cpuIsolation_with_DPDK_MEAN'][1], data['cpuIsolation_with_DPDK_MEAN'][5]
        twoOvs["MEAN"] = data['cpuIsolation_with_DPDK_MEAN'][2], data['cpuIsolation_with_DPDK_MEAN'][6]
        fourOvs["MEAN"] = data['cpuIsolation_with_DPDK_MEAN'][3], 0
        baseline["STD"] = data['cpuIsolation_with_DPDK_STD'][0]*2, data['cpuIsolation_with_DPDK_STD'][4]*2
        oneOvs["STD"] = data['cpuIsolation_with_DPDK_STD'][1]*2, data['cpuIsolation_with_DPDK_STD'][5]*2
        twoOvs["STD"] = data['cpuIsolation_with_DPDK_STD'][2]*2, data['cpuIsolation_with_DPDK_STD'][6]*2
        fourOvs["STD"] = data['cpuIsolation_with_DPDK_STD'][3]*2, 0
        baselineTwo["MEAN"] = data['cpuIsolation_with_DPDK_MEAN'][11], data['cpuIsolation_with_DPDK_MEAN'][13]
        baselineFour["MEAN"] = data['cpuIsolation_with_DPDK_MEAN'][12], data['cpuIsolation_with_DPDK_MEAN'][14]
        baselineTwo["STD"] = data['cpuIsolation_with_DPDK_STD'][11]*2, data['cpuIsolation_with_DPDK_STD'][13]*2
        baselineFour["STD"] = data['cpuIsolation_with_DPDK_STD'][12]*2, data['cpuIsolation_with_DPDK_STD'][14]*2
    return baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour

def plotShared():
    print "plotShared()"
    # Iperf
    Scs = getScs(fIperfBenchmark)
    ipTput = getData(Scs, fIperfBenchmark, "S_Bandwidth")
    # Apache
    Scs = getScs(fAbBenchmark)
    abTput = getData(Scs, fAbBenchmark, "Requests per second")
    Scs = getScs(fAbBenchmark)
    abLat = getData(Scs, fAbBenchmark, " mean")
    # Memcached
    Scs = getScs(fMemBenchmark)
    meTput = getData(Scs, fMemBenchmark, "Throughput")
    Scs = getScs(fMemBenchmark)
    meLat = getData(Scs, fMemBenchmark, "The average response time")
    figureName = "plotbench_shared.pdf"
    # figureName = "plotbench_shared.png"
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(ipTput, "shared")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=1)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(abTput, "shared")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=2)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(meTput, "shared")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=3)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(abLat, "shared")
    plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=4)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(meLat, "shared")
    plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", pltN=5)

def plotIsolated():
    print "plotIsolated()"
    # Iperf
    Scs = getScs(fIperfBenchmark)
    ipTput = getData(Scs, fIperfBenchmark, "S_Bandwidth")
    # Apache
    Scs = getScs(fAbBenchmark)
    abTput = getData(Scs, fAbBenchmark, "Requests per second")
    Scs = getScs(fAbBenchmark)
    abLat = getData(Scs, fAbBenchmark, " mean")
    # Memcached
    Scs = getScs(fMemBenchmark)
    meTput = getData(Scs, fMemBenchmark, "Throughput")
    Scs = getScs(fMemBenchmark)
    meLat = getData(Scs, fMemBenchmark, "The average response time")
    figureName = "plotbench_isolated.pdf"
    # figureName = "plotbench_isolated.png"
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(ipTput, "isolated")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", pltN=1, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(abTput, "isolated")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", pltN=2, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(meTput, "isolated")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", pltN=3, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(abLat, "isolated")
    plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", pltN=4, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(meLat, "isolated")
    plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", pltN=5, baselineTwo=baselineTwo, baselineFour=baselineFour)

def plotDpdk():
    print "plotDpdk()"
    # Iperf
    Scs = getScs(fIperfBenchmark)
    ipTput = getData(Scs, fIperfBenchmark, "S_Bandwidth")
    # Apache
    Scs = getScs(fAbBenchmark)
    abTput = getData(Scs, fAbBenchmark, "Requests per second")
    Scs = getScs(fAbBenchmark)
    abLat = getData(Scs, fAbBenchmark, " mean")
    # Memcached
    Scs = getScs(fMemBenchmark)
    meTput = getData(Scs, fMemBenchmark, "Throughput")
    Scs = getScs(fMemBenchmark)
    meLat = getData(Scs, fMemBenchmark, "The average response time")
    figureName = "plotbench_dpdk.pdf"
    # figureName = "plotbench_dpdk.png"
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(ipTput, "dpdk")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", pltN=1, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(abTput, "dpdk")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", pltN=2, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(meTput, "dpdk")
    plotTput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", pltN=3, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(abLat, "dpdk")
    plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", pltN=4, baselineTwo=baselineTwo, baselineFour=baselineFour)
    baseline, oneOvs, twoOvs, fourOvs, baselineTwo, baselineFour = reorderDict(meLat, "dpdk")
    plotLat(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", pltN=5, baselineTwo=baselineTwo, baselineFour=baselineFour)


if __name__ == "__main__":
    # plotShared()
    # plotIsolated()
    plotDpdk()
