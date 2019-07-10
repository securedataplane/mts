#!/usr/bin/env python
#Author: Kashyap Thimmaraju
#Email: kashyap.thimmaraju@sect-tu-berlin.de
'''
Analyze the latency when vswitch vms are shared
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

figurePath = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/latency-analysis/perVswitch/"
tenants = ["tenant1", "tenant2", "tenant3", "tenant4"]
# tenants = ["tenant1"]
# dicts to store the per tenant latency
b_tLat_p2p = dict.fromkeys(tenants, {})
o_tLat_p2p = dict.fromkeys(tenants, {})
t_tLat_p2p = dict.fromkeys(tenants, {})
f_tLat_p2p = dict.fromkeys(tenants, {})

b_tLat_p2v = dict.fromkeys(tenants, {})
o_tLat_p2v = dict.fromkeys(tenants, {})
t_tLat_p2v = dict.fromkeys(tenants, {})
f_tLat_p2v = dict.fromkeys(tenants, {})

b_tLat_v2v = dict.fromkeys(tenants, {})
o_tLat_v2v = dict.fromkeys(tenants, {})
t_tLat_v2v = dict.fromkeys(tenants, {})
f_tLat_v2v = dict.fromkeys(tenants, {})

def plotLatencyPerVswitch(pcapAnalysisPath, resourceType="shared", topology="p2p"):

    if resourceType == "shared":
        print "tenants" + str(tenants)
        for t in tenants:
            if topology == "p2p":
                b_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-Baseline_NoDPDK-', True, t)
                o_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_OneOvs-', True, t)
                t_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_TwoOvs-', True, t)
                f_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_FourOvs-', True, t)
            elif topology == "p2v":
                b_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-Baseline_NoDPDK-', True, t)
                o_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_OneOvs-', True, t)
                t_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_TwoOvs-', True, t)
                f_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_FourOvs-', True, t)
            elif topology == "v2v":
                if t == "tenant3" or t == "tenant4":
                    continue
                else:
                    b_tLat_v2v[t] = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-Baseline_NoDPDK-', True, t, "v2v")
                    o_tLat_v2v[t] = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_OneOvs-', True, t, "v2v")
                    t_tLat_v2v[t] = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_TwoOvs-', True, t, "v2v")
    # pprint.pprint(two_tLat_p2p[tenants[0]]["64bytes"])

    fig = plt.figure(1, figsize = (8.75, 4.6),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 1, 1)
    # plt.tight_layout()
    c = 0

    data = []
    xmark = []
    c = 0
    labels = ["64bytes"]
    if topology == "p2p":
        for t in tenants:
            data.append(b_tLat_p2p[t][u'64bytes'])
        for t in tenants:
            data.append(o_tLat_p2p[t][u'64bytes'])
        for t in tenants:
            data.append(t_tLat_p2p[t][u'64bytes'])
        for t in tenants:
            data.append(f_tLat_p2p[t][u'64bytes'])
    elif topology == "p2v":
        for t in tenants:
            data.append(b_tLat_p2v[t][u'64bytes'])
        for t in tenants:
            data.append(o_tLat_p2v[t][u'64bytes'])
        for t in tenants:
            data.append(t_tLat_p2v[t][u'64bytes'])
        for t in tenants:
            data.append(f_tLat_p2v[t][u'64bytes'])
    elif topology == "v2v":
        for t in ["tenant1", "tenant2"]:
            data.append(b_tLat_v2v[t][u'64bytes'])
        for t in ["tenant1", "tenant2"]:
            data.append(o_tLat_v2v[t][u'64bytes'])
        for t in ["tenant1", "tenant2"]:
            data.append(t_tLat_v2v[t][u'64bytes'])
    # pprint.pprint(data)
    print "len(data): " + str(len(data))

    plotType = "sortedcdf"
    if plotType == "histogram":
        # For histogram
        print "histogram"
        plt.hist(x=data[8], bins=20, density=False, range=[2,32])
        print len(data[0])
    elif plotType == "cdf":
        # For cdf
        print "cdf"
        values, base = np.histogram(data[0], bins=20, normed=True)
        cumulative = np.cumsum(values)
        print cumulative
        plt.plot(base[1:], cumulative, c='blue')
    elif plotType == "sortedcdf":
        # For sorted cdf
        print "Sortedcdf"
        sorted_data = np.sort(data[0])
        yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
        plt.plot(sorted_data, yvals)
        for d in data:
            for q in [50, 90, 95, 100]:
                print ("{}%% percentile: {}".format(q, np.percentile(d, q)))

    elif plotType == "boxplot":
        # For boxplot
        bp_dict = plt.boxplot(data, patch_artist=False)
        colors = ['black', '#1F77B4', '#FF7F0E', '#2CA02C']
        colors = ['black']
        for color in colors:
            plt.setp(bp_dict['whiskers'], color=color, linewidth=1, linestyle='-')
            plt.setp(bp_dict['fliers'], color=color, linewidth=1, marker='+', markersize=1)
            plt.setp(bp_dict['boxes'], color=color, linewidth=1)
            plt.setp(bp_dict['medians'], linewidth=1, color='red')


        plt.ylim((1,10000))
        plt.ylabel('Latency ($\mu$s)')
        # box = ax.get_position()
        # ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.75])
        ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
        ax.set_axisbelow(True)
        ax.set_yscale('log')

    plt.title("Per tenant latency analysis for "+topology)
    figureName = "plot_lat_pertenant_"+plotType+"_"+resourceType+"_"+topology+".png"
    plt.savefig(figurePath + figureName)

def plotShared():
    print "plotShared()"
    print "plot latency"
    # pcapAnalysisPathLatencyShared = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-submission/latency/sharedCPU/10kppsNic/"
    pcapAnalysisPathLatencyShared = "/tmp/test/"
    plotLatencyPerVswitch(pcapAnalysisPathLatencyShared, resourceType="shared", topology="p2p")

if __name__ == "__main__":
    plotShared()