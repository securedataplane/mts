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

figurePath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/plots/"

def plotResources(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", twobaseline="", fourbaseline=""):
    print "plotResources"
    if resourceType == "shared":
        b = tuple(baseline["shared"])
        one = tuple(oneOvs["shared"])
        two = tuple(twoOvs["shared"])
        four = tuple(fourOvs["shared"])
    elif resourceType == "isolated":
        b = tuple(baseline["isolated"])
        one = tuple(oneOvs["isolated"])
        two = tuple(twoOvs["isolated"])
        four = tuple(fourOvs["isolated"])
        btwo = tuple(twobaseline["isolated"])
        bfour = tuple(fourbaseline["isolated"])
    elif resourceType == "dpdk":
        b = tuple(baseline["dpdk"])
        one = tuple(oneOvs["dpdk"])
        two = tuple(twoOvs["dpdk"])
        four = tuple(fourOvs["dpdk"])
        btwo = tuple(twobaseline["dpdk"])
        bfour = tuple(fourbaseline["dpdk"])

    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5']
    colors = [u'#66c2a5', u'#fa8e63', u'#8da0cb', '#3D9970']
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5' ]
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5', '#7D7D7D', '#B1B1B1' ]
    # fig = plt.figure(1, figsize = (6.974, 2.15512978986403/3.0),frameon=True)
    # fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 3, 3)
    plt.tight_layout()
    width = .1
    N = 2
    ind = np.arange(N)
    ax.yaxis.grid(True, linestyle='-.', which='major')
    if resourceType == "shared":
        rects1 = ax.bar(ind, b, width=width, color=colors[0], edgecolor='none', label="Baseline")
        rects2 = ax.bar(ind + width, one, width=width, color=colors[1], edgecolor='none', label="1 vs-vm")
        rects3 = ax.bar(ind + 2 * width, two, width=width, color=colors[2], edgecolor='none', label="2 vs-vm")
        rects4 = ax.bar(ind + 3 * width, four, width=width, color=colors[3], edgecolor='none', label="4 vs-vm")
    elif resourceType == "isolated" or resourceType == "dpdk":
        rects1 = ax.bar(ind, b, width=width, color=colors[0], edgecolor='none')
        rects2 = ax.bar(ind + width, btwo, width=width, color=colors[4], edgecolor='none')
        rects3 = ax.bar(ind + 2 * width, bfour, width=width, color=colors[5], edgecolor='none')
        rects4 = ax.bar(ind + 4 * width, one, width=width, color=colors[1], edgecolor='none')
        rects5 = ax.bar(ind + 5 * width, two, width=width, color=colors[2], edgecolor='none')
        rects6 = ax.bar(ind + 6 * width, four, width=width, color=colors[3], edgecolor='none')

    plt.ylim((0, 6))
    ax.set_ylabel('Total Resource Units\n(host+vs)')
    if resourceType == "shared":
        ax.set_xlabel('(c)')
    elif resourceType == "isolated":
        ax.set_xlabel('(f)')
    elif resourceType == "dpdk":
        ax.set_xlabel('(i)')
    ax.set_xticks(ind + width + .15)
    if resourceType == "shared":
        ax.set_xticks(ind + width + .05)
        # ax.set_xticklabels(('cpu', 'ram'))
        ax.set_xticklabels((' B MTS\ncpu', 'B MTS\nram'))
    elif resourceType == "isolated" or resourceType == "dpdk":
        ax.set_xticklabels(('    B      MTS\ncpu', '     B      MTS\nram'))
    ax.set_axisbelow(True)

    # box = ax.get_position()
    # ax.set_position([box.x0 + box.width * .1, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])
    # if resourceType == "shared":
    #     ax.legend()
    # plt.show()
    plt.savefig(figurePath + figureName)
    plt.close()

def plotThroughput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared", twobaseline="", fourbaseline=""):
    print "plotThroughput"
    b, one, two, four, btwo, bfour = (), (), (), (), (), ()
    if resourceType == "shared":
        b = tuple(baseline["shared"])
        one = tuple(oneOvs["shared"])
        two = tuple(twoOvs["shared"])
        four = tuple(fourOvs["shared"])
    elif resourceType == "isolated":
        b = tuple(baseline["isolated"])
        one = tuple(oneOvs["isolated"])
        two = tuple(twoOvs["isolated"])
        four = tuple(fourOvs["isolated"])
        btwo = tuple(twobaseline["isolated"])
        bfour = tuple(fourbaseline["isolated"])
    elif resourceType == "dpdk":
        b = tuple(baseline["dpdk"])
        one = tuple(oneOvs["dpdk"])
        two = tuple(twoOvs["dpdk"])
        four = tuple(fourOvs["dpdk"])
        btwo = tuple(twobaseline["dpdk"])
        bfour = tuple(fourbaseline["dpdk"])

    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5']
    colors = [u'#66c2a5', u'#fa8e63', u'#8da0cb', '#3D9970']
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5' ]
    colors = ['#5A5A5A', '#599487', '#CD6320', '#7EA1C5', '#7D7D7D', '#B1B1B1' ]
    fig = plt.figure(1, figsize = (6.974, 2.15512978986403),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 3, 1)
    plt.tight_layout()
    width = .1
    N = 3
    ind = np.arange(N)
    if resourceType == "shared":
        rects1 = ax.bar(ind, b, width=width, color=colors[0], edgecolor='none', label="Baseline")
        rects2 = ax.bar(ind + width, one, width=width, color=colors[1], edgecolor='none', label="1 vs-vm")
        rects3 = ax.bar(ind + 2 * width, two, width=width, color=colors[2], edgecolor='none', label="2 vs-vm")
        rects4 = ax.bar(ind + 3 * width, four, width=width, color=colors[3], edgecolor='none', label="4 vs-vm")
    elif resourceType == "isolated" or resourceType == "dpdk":
        rects1 = ax.bar(ind, b, width=width, color=colors[0], edgecolor='none', label='_nolegend_')
        rects2 = ax.bar(ind + width, btwo, width=width, color=colors[4], edgecolor='none', label="Baseline\n2 cores")
        rects3 = ax.bar(ind + 2 * width, bfour, width=width, color=colors[5], edgecolor='none', label='Baseline\n4 cores')
        rects4 = ax.bar(ind + 4 * width, one, width=width, color=colors[1], edgecolor='none', label='_nolegend_')
        rects5 = ax.bar(ind + 5 * width, two, width=width, color=colors[2], edgecolor='none', label='_nolegend_')
        rects6 = ax.bar(ind + 6 * width, four, width=width, color=colors[3], edgecolor='none', label='_nolegend_')
    if resourceType == "shared":
        plt.ylim((0, 1))
        ax.set_xlabel('(a)')
    elif resourceType == "isolated":
        plt.ylim((0, 4))
        ax.set_xlabel('(d)')
    elif resourceType == "dpdk":
        plt.ylim((0, 15))
        ax.set_xlabel('(g)')
    ax.set_ylabel(resourceType + '\nRx Tput (Mpps)')
    ax.set_xticks(ind + width + .15)
    if resourceType == "shared":
        ax.set_xticks(ind + width + .1)
        # ax.set_xticklabels(('p2p', 'p2v', 'v2v'))
        ax.set_xticklabels((' B MTS\np2p', ' B MTS\np2v', ' B MTS\nv2v'))
    elif resourceType == "isolated" or resourceType == "dpdk":
        ax.set_xticklabels(('   B   MTS\np2p', '    B   MTS\np2v', '    B   MTS\nv2v'))
    ax.set_axisbelow(True)

    box = ax.get_position()
    if resourceType == "shared":
        ax.legend()
    elif resourceType == "isolated":
        ax.legend()
    # ax.set_position([box.x0 + box.width * .12, box.y0 + box.height * .23 , box.width * 0.9, box.height * 0.84])
    # plt.show()
    # plt.close()
    plt.savefig(figurePath + figureName)

def plotLatencySplit(pcapAnalysisPath, figureName, resourceType="shared"):

    if resourceType == "shared":
        b_p2p = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_NoDPDK-')
        one_p2p = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_NoDPDK_OneOvs-')
        two_p2p = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        four_p2p = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_FourOvs-')
        b_p2v = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_NoDPDK-')
        one_p2v = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_NoDPDK_OneOvs-')
        two_p2v = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        four_p2v = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_FourOvs-')
        b_v2v = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-Baseline_NoDPDK-')
        one_v2v = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-SRIOV_NoDPDK_OneOvs-')
        two_v2v = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_TwoOvs-')
        four_v2v = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_FourOvs-')
    if resourceType == "isolated":
        b_p2p = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_NoDPDK-')
        one_p2p = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_NoDPDK_OneOvs-')
        two_p2p = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        four_p2p = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_FourOvs-')
        twob_p2p = read_lat_dict(pcapAnalysisPath+ 'phy2phy-latency-Baseline_NoDPDK_2Core-')
        fourb_p2p = read_lat_dict(pcapAnalysisPath+ 'phy2phy-latency-Baseline_NoDPDK_4Core-')

        b_p2v = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_NoDPDK-')
        one_p2v = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_NoDPDK_OneOvs-')
        two_p2v = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        four_p2v = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_FourOvs-')
        twob_p2v = read_lat_dict(pcapAnalysisPath+ 'phy2vm2vm2phy-latency-Baseline_NoDPDK_2Core-')
        fourb_p2v = read_lat_dict(pcapAnalysisPath+ 'phy2vm2vm2phy-latency-Baseline_NoDPDK_4Core-')

        b_v2v = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-Baseline_NoDPDK-')
        one_v2v = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-SRIOV_NoDPDK_OneOvs-')
        two_v2v = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_TwoOvs-')
        four_v2v = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_FourOvs-')
        twob_v2v = read_lat_dict(pcapAnalysisPath+ 'vm2vm-latency-Baseline_NoDPDK_2Core-')
        fourb_v2v = read_lat_dict(pcapAnalysisPath+ 'vm2vm-latency-Baseline_NoDPDK_4Core-')

    if resourceType == "dpdk":
        b_p2p = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_DPDK-')
        one_p2p = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_DPDK_OneOvs-')
        two_p2p = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_DPDK_TwoOvs-')
        four_p2p = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_DPDK_FourOvs-')
        twob_p2p = read_lat_dict(pcapAnalysisPath+ 'phy2phy-latency-Baseline_DPDK_2Core-')
        fourb_p2p = read_lat_dict(pcapAnalysisPath+ 'phy2phy-latency-Baseline_DPDK_4Core-')

        b_p2v = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_DPDK-')
        one_p2v = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_DPDK_OneOvs-')
        two_p2v = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_DPDK_TwoOvs-')
        four_p2v = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_DPDK_FourOvs-')
        twob_p2v = read_lat_dict(pcapAnalysisPath+ 'phy2vm2vm2phy-latency-Baseline_DPDK_2Core-')
        fourb_p2v = read_lat_dict(pcapAnalysisPath+ 'phy2vm2vm2phy-latency-Baseline_DPDK_4Core-')

        b_v2v = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-Baseline_DPDK-')
        one_v2v = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-SRIOV_DPDK_OneOvs-')
        two_v2v = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_DPDK_TwoOvs-')
        four_v2v = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_DPDK_FourOvs-')
        twob_v2v = read_lat_dict(pcapAnalysisPath+ 'vm2vm-latency-Baseline_DPDK_2Core-')
        fourb_v2v = read_lat_dict(pcapAnalysisPath+ 'vm2vm-latency-Baseline_DPDK_4Core-')

    # fig = plt.figure(1, figsize = (8.75, 4.6),frameon=True)
    # fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 3, 2)
    # plt.tight_layout()

    c = 0

    data = []
    xmark = []
    c = 0
    labels = ["64bytes"]
    for l in labels:
        if resourceType == "shared":
            data.append(b_p2p[l])
            data.append(one_p2p[l])
            data.append(two_p2p[l])
            data.append(four_p2p[l])

            data.append(b_p2v[l])
            data.append(one_p2v[l])
            data.append(two_p2v[l])
            data.append(four_p2v[l])

            data.append(b_v2v[l])
            data.append(one_v2v[l])
            data.append(two_v2v[l])
            data.append(four_v2v[l])
        elif resourceType == "isolated" or resourceType == "dpdk":
            data.append(b_p2p[l])
            data.append(twob_p2p[l])
            data.append(fourb_p2p[l])

            data.append(one_p2p[l])
            data.append(two_p2p[l])
            data.append(four_p2p[l])

            data.append(b_p2v[l])
            data.append(twob_p2v[l])
            data.append(fourb_p2v[l])

            data.append(one_p2v[l])
            data.append(two_p2v[l])
            data.append(four_p2v[l])

            data.append(b_v2v[l])
            data.append(twob_v2v[l])
            data.append(fourb_v2v[l])

            data.append(one_v2v[l])
            data.append(two_v2v[l])
            data.append(four_v2v[l])
    if resourceType == "shared":
        ax.text(0.5, 20000.05, u'B')
        ax.text(1.5, 20000.05, u'1')
        ax.text(2.5, 20000.05, u'2')
        ax.text(3.5, 20000.05, u'4')
        ax.text(4.5, 20000.05, u'B')
        ax.text(5.5, 20000.05, u'1')
        ax.text(6.5, 20000.05, u'2')
        ax.text(7.5, 20000.05, u'4')
        ax.text(8.5, 20000.05, u'B')
        ax.text(9.5, 20000.05, u'1')
        ax.text(10.5, 20000.05, u'2')
        # ax.text(4.0, 100000.05, u'4')
    elif resourceType == "isolated":
        ax.text(0.5, 20000.05, u'1')
        ax.text(1.5, 20000.05, u'2')
        ax.text(2.5, 20000.05, u'4')
        ax.text(3.5, 20000.05, u'1')
        ax.text(4.5, 20000.05, u'2')
        ax.text(5.5, 20000.05, u'4')

        ax.text(6.5, 20000.05, u'1')
        ax.text(7.5, 20000.05, u'2')
        ax.text(8.5, 20000.05, u'4')
        ax.text(9.5, 20000.05, u'1')
        ax.text(10.5, 20000.05, u'2')
        ax.text(11.5, 20000.05, u'4')

        ax.text(12.5, 20000.05, u'1')
        ax.text(13.5, 20000.05, u'2')
        ax.text(14.5, 20000.05, u'4')
        ax.text(15.5, 20000.05, u'1')
        ax.text(16.5, 20000.05, u'2')
        # ax.text(18.0, 20000.05, u'4')

    bp_dict = plt.boxplot(data, patch_artist=False)
    colors = ['black', '#1F77B4', '#FF7F0E', '#2CA02C']
    colors = ['black']
    for color in colors:
        plt.setp(bp_dict['whiskers'], color=color, linewidth=1, linestyle='-')
        plt.setp(bp_dict['fliers'], color=color, linewidth=1, marker='+', markersize=1)
        plt.setp(bp_dict['boxes'], color=color, linewidth=1)
        plt.setp(bp_dict['medians'], linewidth=1, color='red')


    # plt.xticks(range(1, 13), tuple(["B", "1", "2", "4", "B", "1", "2", "4", "B", "1", "2", "4"]))
    if resourceType == "shared":
        # plt.xticks([2.5, 6.5, 10.5], tuple(["p2p", "p2v", "v2v"]))
        plt.xticks([2.5, 6.5, 10.5], tuple(["B MTS\np2p", "B MTS\np2v", "B MTS\nv2v"]))
        plt.plot([4.5, 4.5], [-1, 100000], color='#000000')
        plt.plot([8.5, 8.5], [-1, 100000], color='#000000')
    elif resourceType == "isolated" or resourceType == "dpdk":
        plt.xticks([3, 9, 15], tuple(["    B MTS\np2p", "   B MTS\np2v", "   B MTS\nv2v"]))
        plt.plot([6.5, 6.5], [-1, 100000], color='#000000')
        plt.plot([12.5, 12.5], [-1, 100000], color='#000000')
    # plt.xticks(range(1, 5), tuple(xmark))


    plt.ylim((1,100000))
    plt.ylabel('Latency ($\mu$s)')
    if resourceType == "shared":
        ax.set_xlabel('(b)')
    elif resourceType == "isolated":
        ax.set_xlabel('(e)')
    elif resourceType == "dpdk":
        ax.set_xlabel('(h)')
    # box = ax.get_position()
    # ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.75])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    plt.savefig(figurePath + figureName)
    # plt.close()

def plotShared():
    print "plotShared()"
    print "plot tput"
    figureName = "plot_shared.pdf"
    figureName = "plot_shared.png"
    baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline = tPlotter.getData()
    plotThroughput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared")
    print "plot latency"
    pcapAnalysisPathLatencyShared = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/latency/sharedCPU/10kppsNic/"
    plotLatencySplit(pcapAnalysisPathLatencyShared, figureName, resourceType="shared")
    print "plot resources"
    baseline, oneOvs, twoOvs, fourOvs = {}, {}, {}, {}
    baseline["shared"] = [1, 1]
    oneOvs["shared"] = [2, 2]
    twoOvs["shared"] = [2, 3]
    fourOvs["shared"] = [2, 5]
    plotResources(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="shared")

def plotIsolated():
    print "plotIsolated()"
    print "plot tput"
    figureName = "plot_isolated.pdf"
    figureName = "plot_isolated.png"
    baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline = tPlotter.getData()
    plotThroughput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", twobaseline=twobaseline, fourbaseline=fourbaseline)
    print "plot latency"
    pcapAnalysisPathLatencyIsolated = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/latency/isolatedCPU/10kppsNic/"
    plotLatencySplit(pcapAnalysisPathLatencyIsolated, figureName, resourceType="isolated")
    print "plot resources"
    baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline = {}, {}, {}, {}, {}, {}
    baseline["isolated"] = [1, 1]
    oneOvs["isolated"] = [2, 2]
    twoOvs["isolated"] = [3, 3]
    fourOvs["isolated"] = [5, 5]
    twobaseline["isolated"] = [2, 3]
    fourbaseline["isolated"] = [4, 5]
    plotResources(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="isolated", twobaseline=twobaseline, fourbaseline=fourbaseline)

def plotDpdk():
    print "plotDpdk()"
    print "plot tput"
    figureName = "plot_dpdk.pdf"
    figureName = "plot_dpdk.png"
    baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline = tPlotter.getData()
    plotThroughput(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", twobaseline=twobaseline, fourbaseline=fourbaseline)
    print "plot latency"
    pcapAnalysisPathLatencyDpdk = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-cr-prep/latency/isolatedCPU/10kppsNic/"
    plotLatencySplit(pcapAnalysisPathLatencyDpdk, figureName, resourceType="dpdk")
    print "plot resources"
    baseline, oneOvs, twoOvs, fourOvs, twobaseline, fourbaseline = {}, {}, {}, {}, {}, {}
    baseline["dpdk"] = [2, 1.25]
    oneOvs["dpdk"] = [2, 2]
    twoOvs["dpdk"] = [3, 3]
    fourOvs["dpdk"] = [5, 5]
    twobaseline["dpdk"] = [3, 3]
    fourbaseline["dpdk"] = [5, 5]
    plotResources(baseline, oneOvs, twoOvs, fourOvs, figureName, resourceType="dpdk", twobaseline=twobaseline, fourbaseline=fourbaseline)


if __name__ == "__main__":
    # plotShared()
    # plotIsolated()
    plotDpdk()
