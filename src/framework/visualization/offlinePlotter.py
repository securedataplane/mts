import numpy as np
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy import arange
from scipy.interpolate import spline
from pylab import *
import itertools
import json
import time
import re
from datetime import datetime, tzinfo, timedelta
import glob
from matplotlib.patches import Rectangle


pcapAnalysisPathThroughput = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/nsdi-submission/throughput/sharedCPU/"
pcapAnalysisPathLatency = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/nsdi-submission/latency/sharedCPU/"

pcapAnalysisPathThroughputIsolated = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/nsdi-submission/throughput/isolatedCPU/"
pcapAnalysisPathLatencyIsolated = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/nsdi-submission/latency/isolatedCPU/"

# pcapAnalysisPathLatency = "/tmp/testing/nsdi/latency/sharedCPU/"
experiments = ["throughput", "latency"]
topology = "phy2phy"
topology = "phy2vm2vm2phy"
topologies = ["phy2phy", "phy2vm2vm2phy"]
# topology = "phy2phy"
# topology = "phy2vm2vm2phy"

labels = ["64bytes", "512bytes", "1500bytes", "2048bytes", "9000bytes"]
labels = ["64bytes", "512bytes", "1500bytes", "2048bytes"]
lat_packet_start_index = 500
lat_packet_end_index = 10500

topologies = ["phy2phy", "phy2vm2vm2phy"]
# SRIOV_*_MultiTenant is single OVSVM
vswitchModes = ["Baseline_NoDPDK", "Baseline_DPDK", "SRIOV_NoDPDK", "SRIOV_DPDK",
                "Baseline_MultiTenant_NoDPDK", "Baseline_MultiTenant_DPDK",
                "SRIOV_MultiTenant_NoDPDK", "SRIOV_MultiTenant_DPDK",
                "SRIOV_MultiOvs_NoDPDK", "SRIOV_MultiOvs_DPDK"]

print "topologies: " + str(topologies)
print "vswitchModes: " + str(vswitchModes)

def plotThroughput(pcapAnalysisPath, topology):
    baseline_noDpdk_tx, baseline_noDpdk_rx = [], []
    baseline_Dpdk_tx, baseline_Dpdk_rx = [], []
    sriov_dpdk_tx, sriov_dpdk_rx = [], []
    sriov_noDpdk_tx, sriov_noDpdk_rx = [], []
    if topology == "phy2phy":
        baseline_noDpdk_tx, baseline_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_NoDPDK-planeelbe-*')
        baseline_Dpdk_tx, baseline_Dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_DPDK-planeelbe-*')
        sriov_dpdk_tx, sriov_dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_DPDK-planeelbe-*')
        sriov_noDpdk_tx, sriov_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_NoDPDK-planeelbe-*')
    elif topology == "phy2vm2vm2phy":
        baseline_noDpdk_tx, baseline_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_NoDPDK-planeelbe-*')
        baseline_Dpdk_tx, baseline_Dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_DPDK-planeelbe-*')
        sriov_dpdk_tx, sriov_dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_DPDK-planeelbe-*')
        sriov_noDpdk_tx, sriov_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_NoDPDK-planeelbe-*')
    print baseline_noDpdk_tx, baseline_noDpdk_rx
    print baseline_Dpdk_tx, baseline_Dpdk_rx
    print sriov_dpdk_tx, sriov_dpdk_rx
    print sriov_noDpdk_tx, sriov_noDpdk_rx
    fig = plt.figure(1, figsize=(8.75, 4.6), frameon=True)
    ax = plt.subplot(111)

    plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^'))

    # plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, marker=marker.next(), color='#79c36a', linestyle='', label='baseline_nodpdk', markersize=9)
    # plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, marker=marker.next(), color='#79c36a', linestyle='', label='baseline_dpdk', markersize=9)
    # plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, marker=marker.next(), color='#599ad3', linestyle='', label='sriov_nodpdk', markersize=9)
    # plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, marker=marker.next(), color='#727272', linestyle='', label='sriov_dpdk', markersize=9)
    plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, label='baseline_nodpdk', marker=marker.next(), linestyle='')
    plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, label='baseline_dpdk', marker=marker.next(), linestyle='')
    plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, label='sriov_nodpdk', marker=marker.next(), linestyle='')
    plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, label='sriov_dpdk', marker=marker.next(), linestyle='')

    # plt.ylim((300000, 700000 + 20000))
    # plt.xlim((300000, 1500000 + 20000))
    plt.ylabel('Packets/s Forwarded (k packets/s)')
    plt.xlabel("Offered load (k packets/s)")

    ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.45), numpoints=1)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'.png', dpi=(250), format='png')
    plt.close()

def plotThroughputMulti(pcapAnalysisPath, topology):
    Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = [], []
    Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = [], []
    SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = [], []
    SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = [], []
    SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = [], []
    SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = [], []
    SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = [], []
    SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = [], []
    if topology == "phy2phy":
        Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_NoDPDK-planeelbe-*')
        Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_NoDPDK-planeelbe-*')
        SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
    elif topology == "phy2vm2vm2phy":
        Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_NoDPDK-planeelbe-*')
        Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_NoDPDK-planeelbe-*')
        SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
    print Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx
    print Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx
    print SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx
    print SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx
    print SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx
    print SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx
    fig = plt.figure(1, figsize=(8.75, 4.6), frameon=True)
    ax = plt.subplot(111)

    plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^', 'p'))

    # plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, marker=marker.next(), color='#79c36a', linestyle='', label='Baseline_MultiTenant_NoDPDK', markersize=9)
    # plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, marker=marker.next(), color='#599ad3', linestyle='', label='SRIOV_MultiTenant_DPDK', markersize=9)
    # plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, marker=marker.next(), color='#727272', linestyle='', label='SRIOV_MultiTenant_NoDPDK', markersize=9)
    # plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, marker=marker.next(), color='#599ad3', linestyle='',
    #          label='SRIOV_MultiOvs_DPDK', markersize=9)
    # plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, marker=marker.next(), color='#727272',
    #          linestyle='', label='SRIOV_MultiOvs_NoDPDK', markersize=9)
    plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, label='Baseline_MultiTenant_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx, label='Baseline_MultiTenant_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, label='SRIOV_MultiTenant_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, label='SRIOV_MultiTenant_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, label='SRIOV_MultiOvs_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, label='SRIOV_MultiOvs_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx, label='SRIOV_MultiOvs_NoDPDK_Isolated', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx, label='SRIOV_MultiOvs_DPDK_Isolated', marker=marker.next(), linestyle='')


    # plt.ylim((300000, 1400000 + 20000))
    # plt.xlim((300000, 1400000 + 20000))
    plt.ylabel('Packets/s Forwarded (k packets/s)')
    plt.xlabel("Offered load (k packets/s)")

    ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.45), numpoints=1)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi.png', dpi=(320), format='png')
    plt.close()

def plotThroughputSplit(pcapAnalysisPath, topology):
    baseline_noDpdk_tx, baseline_noDpdk_rx = [], []
    baseline_Dpdk_tx, baseline_Dpdk_rx = [], []
    sriov_dpdk_tx, sriov_dpdk_rx = [], []
    sriov_noDpdk_tx, sriov_noDpdk_rx = [], []
    if topology == "phy2phy":
        baseline_noDpdk_tx, baseline_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_NoDPDK-planeelbe-*')
        baseline_Dpdk_tx, baseline_Dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_DPDK-planeelbe-*')
        sriov_dpdk_tx, sriov_dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_DPDK-planeelbe-*')
        sriov_noDpdk_tx, sriov_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_NoDPDK-planeelbe-*')
    elif topology == "phy2vm2vm2phy":
        baseline_noDpdk_tx, baseline_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_NoDPDK-planeelbe-*')
        baseline_Dpdk_tx, baseline_Dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_DPDK-planeelbe-*')
        sriov_dpdk_tx, sriov_dpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_DPDK-planeelbe-*')
        sriov_noDpdk_tx, sriov_noDpdk_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_NoDPDK-planeelbe-*')
    print baseline_noDpdk_tx, baseline_noDpdk_rx
    print baseline_Dpdk_tx, baseline_Dpdk_rx
    print sriov_dpdk_tx, sriov_dpdk_rx
    print sriov_noDpdk_tx, sriov_noDpdk_rx

    fig = plt.figure(1, figsize = (3.487, 2.15512978986403),frameon=True)
    ax = plt.subplot(1, 2, 1)
    plt.tight_layout()

    plt.grid(True)
    # marker = itertools.cycle(('+', '.', 'x', '4'))
    marker = itertools.cycle(('.', '+', 'x', '_', '1', '2', '3', '4'))

    plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, label='Baseline', marker=marker.next(), linestyle='', fillstyle="none", color="black")
    # plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, label='baseline_dpdk', marker=marker.next(), linestyle='')
    plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, label='1 vswitch VM', marker=marker.next(), linestyle='', fillstyle="none")
    # plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, label='sriov_dpdk', marker=marker.next(), linestyle='')

    if topology == "phy2vm2vm2phy":
        plt.ylim((0, 1400))
    else:
        plt.ylim((400, 1400))
    # plt.xlim((400, 1400))
    plt.xticks(range(400, 1500, 400), tuple(range(400, 1500, 400)))
    plt.ylabel('Received load (k packets/s)')
    # plt.xlabel("Offered load (k packets/s)")
    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.90, box.height * 0.75])
    # ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(-0.315, -0.5), numpoints=1)
    ax.set_axisbelow(True)
    plt.figlegend(loc='lower center', ncol=2)

    ### Second plot with dpdk
    ax = plt.subplot(1, 2, 2)
    plt.grid(True)

    marker = itertools.cycle(('.', '+', 'x', '_', '1', '2', '3', '4'))

    # plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, label='B: Baseline', marker=marker.next(), linestyle='', fillstyle="none")
    plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, label='Baseline', marker=marker.next(), linestyle='', fillstyle="none", color="black")
    # plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, label='P1: Principle 1', marker=marker.next(), linestyle='', fillstyle="none")
    plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, label='1 vswitch VM', marker=marker.next(), linestyle='', fillstyle="none")

    if topology == "phy2vm2vm2phy":
        plt.ylim((0, 1400))
    else:
        plt.ylim((400, 1400))
    # plt.ylim((400, 1400))
    plt.xticks(range(400, 1500, 400), tuple(range(400, 1500, 400)))
    plt.figtext(0.35, 0.2, "Offered load (k packets/s)", color="black")

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * .90, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.figtext(0.26, 0.12, "No DPDK", color="black")
    plt.figtext(0.71, 0.12, "With DPDK", color="black")

    # plt.figlegend(loc='lower center', ncol=2)#, bbox_to_anchor=(-0.315, -0.5), numpoints=1)
    # ax.legend(marker, ['Baseline', 'Principle 1', 'Baselin + 3', 'Principle 1 + 3'], handletextpad=-0.18, handlelength=0, markerscale=0, loc='lower center', ncol=3, bbox_to_anchor=(-0.315, -0.5), numpoints=1)


    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Split.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Split.png', dpi=(250), format='png')
    plt.close()

def plotThroughputMultiSplit(pcapAnalysisPath, topology):
    Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = [], []
    Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = [], []
    SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = [], []
    SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = [], []
    SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = [], []
    SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = [], []
    SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = [], []
    SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = [], []
    if topology == "phy2phy":
        Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_NoDPDK-planeelbe-*')
        Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_NoDPDK-planeelbe-*')
        SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
    elif topology == "phy2vm2vm2phy":
        Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_NoDPDK-planeelbe-*')
        Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_NoDPDK-planeelbe-*')
        SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = get_tput_dict(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
    print Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx
    print Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx
    print SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx
    print SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx
    print SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx
    print SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx

    fig = plt.figure(1, figsize = (3.487, 2.15512978986403),frameon=True)
    ax = plt.subplot(1, 2, 1)
    plt.tight_layout()

    plt.grid(True)
    # marker = itertools.cycle(('+', '.', 'x', '_', '1', '2', '3', '4'))
    marker = itertools.cycle(('.', '+', 'x', '_', '1', '2', '3', '4'))

    plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, label='Baseline', marker=marker.next(), linestyle='', fillstyle="none", color="black")
    # plt.plot(Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx, label='Baseline_MultiTenant_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, label='1 vswitch VM', marker=marker.next(), linestyle='', fillstyle="none")
    # plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, label='SRIOV_MultiTenant_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, label='2 vswitch VMs (shared CPU)', marker=marker.next(), linestyle='', fillstyle="none")
    # plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, label='SRIOV_MultiOvs_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx, label='2 vswitch VMs (isolated CPU)', marker=marker.next(), linestyle='', fillstyle="none")
    # plt.plot(SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx, label='SRIOV_MultiOvs_DPDK_Isolated', marker=marker.next(), linestyle='')

    if topology == "phy2vm2vm2phy":
        plt.ylim((0, 1400))
    else:
        plt.ylim((400, 1400))
    # plt.xlim((400, 1400))
    plt.xticks(range(400, 1500, 400), tuple(range(400, 1500, 400)))
    plt.ylabel('Received load (k packets/s)')
    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.29, box.width * 0.90, box.height * 0.75])
    # ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(-0.315, -0.5), numpoints=1)
    ax.set_axisbelow(True)
    plt.figlegend(loc='lower center', ncol=2, handletextpad=-0.18)

    ### Second plot with dpdk
    ax = plt.subplot(1, 2, 2)
    plt.grid(True)
    marker = itertools.cycle(('.', '+', 'x', '_', '1', '2', '3', '4'))

    # plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, label='Baseline_MultiTenant_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx, label='Baseline', marker=marker.next(), linestyle='', fillstyle="none", color="black")
    # plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, label='SRIOV_MultiTenant_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, label='1 vswitch VM', marker=marker.next(), linestyle='', fillstyle="none")
    # plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, label='SRIOV_MultiOvs_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, label='2 vswitch VM (shared CPU) + 3', marker=marker.next(), linestyle='', fillstyle="none")
    # plt.plot(SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx, label='SRIOV_MultiOvs_NoDPDK_Isolated', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx, label='2 vswitch VM (isolated CPU)', marker=marker.next(), linestyle='', fillstyle="none")

    if topology == "phy2vm2vm2phy":
        plt.ylim((0, 1400))
    else:
        plt.ylim((400, 1400))
    plt.xticks(range(400, 1500, 400), tuple(range(400, 1500, 400)))
    plt.figtext(0.35, 0.24, "Offered load (k packets/s)", color="black")

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.29, box.width * .90, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.figtext(0.26, 0.19, "No DPDK", color="black")
    plt.figtext(0.71, 0.19, "With DPDK", color="black")

    # plt.figlegend(loc='lower center', ncol=2, handletextpad=-0.18)#, bbox_to_anchor=(-0.315, -0.5), numpoints=1)

    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi-Split.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi-Split.png', dpi=(320), format='png')
    plt.close()

def get_tput_dict(txPath, rxPath):
    print "get_tput_dict()"
    x1 = []
    y1 = []
    try:
        d = glob.glob(rxPath)
        d.sort()
        for i in d:
            # print "y1 parsedicts:"
            y1.append(parse_tput_dict(i))
            print parse_tput_dict(i)
        d = glob.glob(txPath)
        d.sort()
        for i in d:
            # print "x1 parsedicts:"
            x1.append(parse_tput_dict(i))
            print parse_tput_dict(i)
        # exit()
        return x1, y1
    except:
        x1 = []
        y1 = []

def plotThroughputLoss(pcapAnalysisPath, topology):
    baseline_noDpdk_tx, baseline_noDpdk_rx = [], []
    baseline_Dpdk_tx, baseline_Dpdk_rx = [], []
    sriov_dpdk_tx, sriov_dpdk_rx = [], []
    sriov_noDpdk_tx, sriov_noDpdk_rx = [], []
    if topology == "phy2phy":
        baseline_noDpdk_tx, baseline_noDpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_NoDPDK-planeelbe-*')
        baseline_Dpdk_tx, baseline_Dpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_DPDK-planeelbe-*')
        sriov_dpdk_tx, sriov_dpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_DPDK-planeelbe-*')
        sriov_noDpdk_tx, sriov_noDpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_NoDPDK-planeelbe-*')
    elif topology == "phy2vm2vm2phy":
        baseline_noDpdk_tx, baseline_noDpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_NoDPDK-planeelbe-*')
        baseline_Dpdk_tx, baseline_Dpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_DPDK-planeelbe-*')
        sriov_dpdk_tx, sriov_dpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_DPDK-planeelbe-*')
        sriov_noDpdk_tx, sriov_noDpdk_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_NoDPDK-planeelbe-*')
    print baseline_noDpdk_tx, baseline_noDpdk_rx
    print baseline_Dpdk_tx, baseline_Dpdk_rx
    print sriov_dpdk_tx, sriov_dpdk_rx
    print sriov_noDpdk_tx, sriov_noDpdk_rx
    fig = plt.figure(1, figsize=(8.75, 4.6), frameon=True)
    ax = plt.subplot(111)

    plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^'))

    # plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, marker=marker.next(), color='#79c36a', linestyle='', label='baseline_nodpdk', markersize=9)
    # plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, marker=marker.next(), color='#79c36a', linestyle='', label='baseline_dpdk', markersize=9)
    # plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, marker=marker.next(), color='#599ad3', linestyle='', label='sriov_nodpdk', markersize=9)
    # plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, marker=marker.next(), color='#727272', linestyle='', label='sriov_dpdk', markersize=9)
    plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, label='baseline_nodpdk', marker=marker.next(), linestyle='')
    plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, label='baseline_dpdk', marker=marker.next(), linestyle='')
    plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, label='sriov_nodpdk', marker=marker.next(), linestyle='')
    plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, label='sriov_dpdk', marker=marker.next(), linestyle='')

    # plt.ylim((300000, 700000 + 20000))
    # plt.xlim((300000, 1500000 + 20000))
    plt.ylim((0.000,0.99))
    # plt.xlim((10000,35000))
    plt.ylabel('Packet Loss$(Percent)$')
    plt.xlabel("Packets/s Sent")

    ax.set_yscale('symlog')

    ax.set_yticks((0.00, 0.01, 0.10, 0.20, 0.30, 0.40)) #, ("5\%", "10\%", "15\%", "20\%", "25\%", "30\%", "35\%", "40\%", "45\%", "50\%"))
    ax.set_yticklabels(('0%', '1%', '10%', '20%', '30%', '40%'))
    # ax.set_xticklabels(('k', '15k', '20k', '25k', '30k', '35k'))

    ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.45), numpoints=1)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Loss.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Loss.png', dpi=(250), format='png')
    plt.close()

def plotThroughputMultiLoss(pcapAnalysisPath, topology):
    Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = [], []
    Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = [], []
    SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = [], []
    SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = [], []
    SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = [], []
    SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = [], []
    SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = [], []
    SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = [], []
    if topology == "phy2phy":
        Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_NoDPDK-planeelbe-*')
        Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-Baseline_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_NoDPDK-planeelbe-*')
        SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
    elif topology == "phy2vm2vm2phy":
        Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_NoDPDK-planeelbe-*')
        Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-Baseline_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_NoDPDK-planeelbe-*')
        SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiTenant_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = get_tput_dict_loss(
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPath+'phy2vm2vm2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
        SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_NoDPDK-planeelbe-*')
        SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx = get_tput_dict(
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-elbeplane-*',
            pcapAnalysisPathThroughputIsolated+'phy2phy-throughput-SRIOV_MultiOvs_DPDK-planeelbe-*')
    print Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx
    print Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx
    print SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx
    print SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx
    print SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx
    print SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx
    fig = plt.figure(1, figsize=(8.75, 4.6), frameon=True)
    ax = plt.subplot(111)

    plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^', 'p'))

    # plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, marker=marker.next(), color='#79c36a', linestyle='', label='Baseline_MultiTenant_NoDPDK', markersize=9)
    # plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, marker=marker.next(), color='#599ad3', linestyle='', label='SRIOV_MultiTenant_DPDK', markersize=9)
    # plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, marker=marker.next(), color='#727272', linestyle='', label='SRIOV_MultiTenant_NoDPDK', markersize=9)
    # plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, marker=marker.next(), color='#599ad3', linestyle='',
    #          label='SRIOV_MultiOvs_DPDK', markersize=9)
    # plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, marker=marker.next(), color='#727272',
    #          linestyle='', label='SRIOV_MultiOvs_NoDPDK', markersize=9)
    plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, label='Baseline_MultiTenant_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx, label='Baseline_MultiTenant_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, label='SRIOV_MultiTenant_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, label='SRIOV_MultiTenant_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, label='SRIOV_MultiOvs_NoDPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, label='SRIOV_MultiOvs_DPDK', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_NoDPDK_Isolated_tx, SRIOV_MultiOvs_NoDPDK_Isolated_rx, label='SRIOV_MultiOvs_NoDPDK_Isolated', marker=marker.next(), linestyle='')
    plt.plot(SRIOV_MultiOvs_DPDK_Isolated_tx, SRIOV_MultiOvs_DPDK_Isolated_rx, label='SRIOV_MultiOvs_DPDK_Isolated', marker=marker.next(), linestyle='')


    # plt.ylim((300000, 700000 + 20000))
    # plt.xlim((300000, 1500000 + 20000))
    plt.ylim((0.000,0.99))
    # plt.xlim((10000,35000))
    plt.ylabel('Packet Loss$(Percent)$')
    plt.xlabel("Packets/s Sent")

    ax.set_yscale('symlog')

    ax.set_yticks((0.00, 0.01, 0.10, 0.20, 0.30, 0.40)) #, ("5\%", "10\%", "15\%", "20\%", "25\%", "30\%", "35\%", "40\%", "45\%", "50\%"))
    ax.set_yticklabels(('0%', '1%', '10%', '20%', '30%', '40%'))
    # ax.set_xticklabels(('k', '15k', '20k', '25k', '30k', '35k'))

    ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.45), numpoints=1)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi-Loss.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi-Loss.png', dpi=(320), format='png')
    plt.close()

def get_tput_dict_loss(txPath, rxPath):
    print "get_tput_dict()"
    x1 = []
    x11 = []
    y1 = []
    try:
        d = glob.glob(txPath)
        d.sort()
        print d
        for i in d:
            print i
            temp = i.split('-')[5]
            print "temp: " + str(temp)
            nmbr = int(temp)
            # nmbr = int(float(temp.split('-')[5]))
            z = parse_tput_dict(i) * 1000
            print z
            x11.append(z)
            x1.append(nmbr)
            print str(parse_tput_dict(i))
        d = glob.glob(rxPath)
        d.sort()
        c1 = 0
        for i in d:
            c2 = 1 - float(parse_tput_dict(i)*1000) / x11[c1]
            y1.append(c2)
            #y1.append(parse_dicts(i))
            c1 = c1 + 1
        return x1, y1
    except:
        x1 = []
        y1 = []

def parse_tput_dict(dict_data):
    for l in open(dict_data):
        if l.split()[0] == 'Average':
            return int(float(l.split()[3])/1000)

def plotLatency(pcapAnalysisPath,topology):
    baseline_noDpdk = {}
    baseline_Dpdk = {}
    sriov_dpdk = {}
    sriov_noDpdk = {}
    if topology == "phy2phy":
        baseline_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_NoDPDK-')
        baseline_Dpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_DPDK-')
        sriov_dpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_DPDK-')
        sriov_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_NoDPDK-')
    elif topology == "phy2vm2vm2phy":
        baseline_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_NoDPDK-')
        baseline_Dpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_DPDK-')
        sriov_dpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_DPDK-')
        sriov_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_NoDPDK-')
    # print baseline_noDpdk
    # print sriov_dpdk
    # print sriov_noDpdk
    fig = plt.figure(1, figsize = (8.75,4.6),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(111)

    c = 0

    data = []
    xmark = []
    data.append([])
    xmark.append("")
    c = 0

    for l in labels:
        data.append(baseline_noDpdk[l])
        xmark.append('baseline-nodpdk')
        data.append(baseline_Dpdk[l])
        xmark.append('baseline-dpdk')
        data.append(sriov_noDpdk[l])
        xmark.append('sriov-nodpdk')
        data.append(sriov_dpdk[l])
        xmark.append('sriov-dpdk')
    ax.text(3.0, 10000.05, u'64$B$')
    ax.text(7.0, 10000.05, u'512$B$')
    ax.text(11.0, 10000.05, u'1500$B$')
    ax.text(15.0, 10000.05, u'2048$B$')
    # ax.text(18.0, 10000.05, u'9000$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=2)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 19), tuple(xmark), rotation='-45', ha='left')

    # Print median values for debug
    # medians=[]
    # for line in bp_dict['medians']:
    #    # get position data for median line
    #    x, y = line.get_xydata()[1] # top of median line
    #    # overlay median value
    #    text(x, y, '%.4f' % y,
    #         horizontalalignment='center', fontsize=5) # draw above, centered
    #    print "%.4f" % y
    #    medians.append(y)

    # plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^'))

    plt.plot([1.0, 1.0], [-1, 10000], color='#000000')
    plt.plot([5.5, 5.5], [-1, 10000], color='#000000')
    plt.plot([9.5, 9.5], [-1, 10000], color='#000000')
    plt.plot([13.5, 13.5], [-1, 10000], color='#000000')
    plt.plot([17.5, 17.5], [-1, 10000], color='#000000')

    plt.ylim((0.001,10))
    plt.ylabel('Latency in millisecond')
    plt.xlabel("Scenario mode")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.78])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')
    # ax.set_xscale('log')

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'.png', dpi=(250), format='png')
    plt.close()

def plotLatencySplitSingles(pcapAnalysisPath,topology):
    baseline_noDpdk = {}
    baseline_Dpdk = {}
    sriov_dpdk = {}
    sriov_noDpdk = {}
    if topology == "phy2phy":
        baseline_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_NoDPDK-')
        baseline_Dpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_DPDK-')
        sriov_dpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_DPDK-')
        sriov_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_NoDPDK-')
    elif topology == "phy2vm2vm2phy":
        baseline_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_NoDPDK-')
        baseline_Dpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_DPDK-')
        sriov_dpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_DPDK-')
        sriov_noDpdk = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_NoDPDK-')
    # print baseline_noDpdk
    # print sriov_dpdk
    # print sriov_noDpdk
    fig = plt.figure(1, figsize = (3.487, 2.15512978986403),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 2, 1)
    plt.tight_layout()

    c = 0

    data = []
    xmark = []
    c = 0

    labels = ["64bytes"]
    for l in labels:
        data.append(baseline_noDpdk[l])
        xmark.append('Baseline')
        # data.append(baseline_Dpdk[l])
        # xmark.append('baseline-dpdk')
        data.append(sriov_noDpdk[l])
        xmark.append('  1 vswitch\nVM')
        # data.append(sriov_dpdk[l])
        # xmark.append('sriov-dpdk')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=1)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks([1, 2], tuple(["B", "1"]))

    plt.plot([1.5, 1.5], [-1, 10000], color='#000000')

    # plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,10000))
    plt.ylabel('Latency (microsecond)')

    # ax.add_patch(Rectangle((1.49, .9), 1, 10002, alpha=0.1, color='blue'))
    # ax.add_patch(Rectangle((2.49, .9), 1, 10002, alpha=0.1, color='orange'))
    # ax.add_patch(Rectangle((3.49, .9), 1, 10002, alpha=0.1, color='green'))

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.80])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    ### Second plot with dpdk
    ax = plt.subplot(1, 2, 2)
    c = 0

    data = []
    xmark = []
    # data.append([])
    # xmark.append("")
    c = 0

    for l in labels:
        # data.append(baseline_noDpdk[l])
        # xmark.append('baseline-nodpdk')
        data.append(baseline_Dpdk[l])
        xmark.append('Baseline')
        # data.append(sriov_noDpdk[l])
        # xmark.append('sriov-nodpdk')
        data.append(sriov_dpdk[l])
        xmark.append('  1 vswitch\nVM')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=1)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks([1, 2], tuple(["B", "1"]))

    plt.plot([1.5, 1.5], [-1, 10000], color='#000000')

    # plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,10000))
    # plt.ylabel('Latency (microsecond)')

    # ax.add_patch(Rectangle((1.49, .9), 1, 10002, alpha=0.1, color='blue'))
    # ax.add_patch(Rectangle((2.49, .9), 1, 10002, alpha=0.1, color='orange'))
    # ax.add_patch(Rectangle((3.49, .9), 1, 10002, alpha=0.1, color='green'))

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.80])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    plt.figtext(0.26, 0.209, "No DPDK", color="black")
    plt.figtext(0.72, 0.209, "With DPDK", color="black")

    ax.legend(['B: Baseline', '1: 1 vswitch VM'], handletextpad=-0.1, handlelength=0, markerscale=0, loc='lower center', ncol=2, bbox_to_anchor=(-0.315, -0.5), numpoints=1)

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-SplitSingles.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-SplitSingles.png', dpi=(250), format='png')
    plt.close()

def plotLatencyMulti(pcapAnalysisPath,topology):
    Baseline_MultiTenant_NoDPDK = {}
    Baseline_MultiTenant_DPDK = {}
    SRIOV_MultiTenant_NoDPDK = {}
    SRIOV_MultiTenant_DPDK = {}
    SRIOV_MultiOvs_DPDK = {}
    SRIOV_MultiOvs_NoDPDK = {}
    SRIOV_MultiOvs_NoDPDK_Isolated = {}
    SRIOV_MultiOvs_DPDK_Isolated = {}

    if topology == "phy2phy":
        Baseline_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_MultiTenant_NoDPDK-')
        Baseline_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_MultiTenant_DPDK-')
        SRIOV_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_MultiTenant_DPDK-')
        SRIOV_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_MultiTenant_NoDPDK-')
        SRIOV_MultiOvs_DPDK = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_MultiOvs_DPDK-')
        SRIOV_MultiOvs_NoDPDK = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_NoDPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_DPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2phy-latency-SRIOV_MultiOvs_DPDK-')
    elif topology == "phy2vm2vm2phy":
        Baseline_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_MultiTenant_NoDPDK-')
        Baseline_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_MultiTenant_DPDK-')
        SRIOV_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_MultiTenant_DPDK-')
        SRIOV_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_MultiTenant_NoDPDK-')
        SRIOV_MultiOvs_DPDK = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_MultiOvs_DPDK-')
        SRIOV_MultiOvs_NoDPDK = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_NoDPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2vm2vm2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_DPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2vm2vm2phy-latency-SRIOV_MultiOvs_DPDK-')
    # print Baseline_MultiTenant_NoDPDK
    # print SRIOV_MultiTenant_DPDK
    # print SRIOV_MultiTenant_NoDPDK
    # print SRIOV_MultiOvs_DPDK
    # print SRIOV_MultiOvs_NoDPDK
    fig = plt.figure(1, figsize = (8.75,4.6),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(111)

    c = 0

    data = []
    xmark = []
    data.append([])
    xmark.append("")
    c = 0

    for l in labels:
        data.append(Baseline_MultiTenant_NoDPDK[l])
        xmark.append('Baseline_MultiTenant_NoDPDK')
        data.append(Baseline_MultiTenant_DPDK[l])
        xmark.append('Baseline_MultiTenant_DPDK')
        data.append(SRIOV_MultiTenant_NoDPDK[l])
        xmark.append('SRIOV_MultiTenant_NoDPDK')
        data.append(SRIOV_MultiTenant_DPDK[l])
        xmark.append('SRIOV_MultiTenant_DPDK')
        data.append(SRIOV_MultiOvs_NoDPDK[l])
        xmark.append('SRIOV_MultiOvs_NoDPDK')
        data.append(SRIOV_MultiOvs_DPDK[l])
        xmark.append('SRIOV_MultiOvs_DPDK')
        data.append(SRIOV_MultiOvs_NoDPDK_Isolated[l])
        xmark.append('SRIOV_MultiOvs_NoDPDK_Isolated')
        data.append(SRIOV_MultiOvs_DPDK_Isolated[l])
        xmark.append('SRIOV_MultiOvs_DPDK_Isolated')
    ax.text(6.0, 10000.05, u'64$B$')
    ax.text(12.0, 10000.05, u'512$B$')
    ax.text(18.0, 10000.05, u'1500$B$')
    ax.text(23.0, 10000.05, u'2048$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=2)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 35), tuple(xmark), rotation='-45', ha='left')

    # Print median values for debug
    # medians=[]
    # for line in bp_dict['medians']:
    #    # get position data for median line
    #    x, y = line.get_xydata()[1] # top of median line
    #    # overlay median value
    #    text(x, y, '%.4f' % y,
    #         horizontalalignment='center', fontsize=5) # draw above, centered
    #    print "%.4f" % y
    #    medians.append(y)

    # plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^'))

    plt.plot([1.0, 1.0], [-1, 10000], color='#000000')
    plt.plot([9.5, 9.5], [-1, 10000], color='#000000')
    plt.plot([17.5, 17.5], [-1, 10000], color='#000000')
    plt.plot([25.5, 25.5], [-1, 10000], color='#000000')
    plt.plot([33.5, 33.5], [-1, 10000], color='#000000')

    plt.ylim((0.001,10))
    plt.ylabel('Latency in millisecond')
    plt.xlabel("Scenario mode")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.78])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')
    # ax.set_xscale('log')

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-Multi.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-Multi.png', dpi=(250), format='png')
    plt.close()

def plotLatencyMultiSplit(pcapAnalysisPath,topology):
    Baseline_MultiTenant_NoDPDK = {}
    Baseline_MultiTenant_DPDK = {}
    SRIOV_MultiTenant_NoDPDK = {}
    SRIOV_MultiTenant_DPDK = {}
    SRIOV_MultiOvs_DPDK = {}
    SRIOV_MultiOvs_NoDPDK = {}
    SRIOV_MultiOvs_NoDPDK_Isolated = {}
    SRIOV_MultiOvs_DPDK_Isolated = {}

    if topology == "phy2phy":
        Baseline_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_MultiTenant_NoDPDK-')
        Baseline_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_MultiTenant_DPDK-')
        SRIOV_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_MultiTenant_DPDK-')
        SRIOV_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_MultiTenant_NoDPDK-')
        SRIOV_MultiOvs_DPDK = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_MultiOvs_DPDK-')
        SRIOV_MultiOvs_NoDPDK = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_NoDPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_DPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2phy-latency-SRIOV_MultiOvs_DPDK-')
    elif topology == "phy2vm2vm2phy":
        Baseline_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_MultiTenant_NoDPDK-')
        Baseline_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_MultiTenant_DPDK-')
        SRIOV_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_MultiTenant_DPDK-')
        SRIOV_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_MultiTenant_NoDPDK-')
        SRIOV_MultiOvs_DPDK = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_MultiOvs_DPDK-')
        SRIOV_MultiOvs_NoDPDK = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_NoDPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2vm2vm2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_DPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2vm2vm2phy-latency-SRIOV_MultiOvs_DPDK-')
    # print Baseline_MultiTenant_NoDPDK
    # print SRIOV_MultiTenant_DPDK
    # print SRIOV_MultiTenant_NoDPDK
    # print SRIOV_MultiOvs_DPDK
    # print SRIOV_MultiOvs_NoDPDK
    fig = plt.figure(1, figsize = (3.487, 2.15512978986403),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 2, 1)
    plt.tight_layout()

    c = 0

    data = []
    xmark = []
    # data.append([])
    # xmark.append("")
    c = 0
    labels = ["64bytes"]
    for l in labels:
        data.append(Baseline_MultiTenant_NoDPDK[l])
        xmark.append('B')
        # data.append(Baseline_MultiTenant_DPDK[l])
        # xmark.append('Baseline_MultiTenant_DPDK')
        data.append(SRIOV_MultiTenant_NoDPDK[l])
        xmark.append('P1')
        # data.append(SRIOV_MultiTenant_DPDK[l])
        # xmark.append('SRIOV_MultiTenant_DPDK')
        data.append(SRIOV_MultiOvs_NoDPDK[l])
        xmark.append('P2.1')
        # data.append(SRIOV_MultiOvs_DPDK[l])
        # xmark.append('SRIOV_MultiOvs_DPDK')
        data.append(SRIOV_MultiOvs_NoDPDK_Isolated[l])
        xmark.append('P2.2')
        # data.append(SRIOV_MultiOvs_DPDK_Isolated[l])
        # xmark.append('SRIOV_MultiOvs_DPDK_Isolated')
    # ax.text(6.0, 10000.05, u'64$B$')
    # ax.text(12.0, 10000.05, u'512$B$')
    # ax.text(18.0, 10000.05, u'1500$B$')
    # ax.text(23.0, 10000.05, u'2048$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=1)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 5), tuple(xmark))

    # Print median values for debug
    # medians=[]
    # for line in bp_dict['medians']:
    #    # get position data for median line
    #    x, y = line.get_xydata()[1] # top of median line
    #    # overlay median value
    #    text(x, y, '%.4f' % y,
    #         horizontalalignment='center', fontsize=5) # draw above, centered
    #    print "%.4f" % y
    #    medians.append(y)

    # plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^'))

    # plt.plot([1.0, 1.0], [-1, 10000], color='#000000')
    plt.plot([1.5, 1.5], [-1, 10000], color='#000000')
    # plt.plot([9.5, 9.5], [-1, 10000], color='#000000')
    # plt.plot([17.5, 17.5], [-1, 10000], color='#000000')
    # plt.plot([25.5, 25.5], [-1, 10000], color='#000000')
    # plt.plot([33.5, 33.5], [-1, 10000], color='#000000')
    plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,10000))
    plt.ylabel('Latency (microsecond)')
    # plt.xlabel("No DPDK")

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.80])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')
    # ax.set_xscale('log')

    ### Second plot with dpdk
    ax = plt.subplot(1, 2, 2)
    c = 0

    data = []
    xmark = []
    # data.append([])
    # xmark.append("")
    c = 0
    labels = ["64bytes"]
    for l in labels:
        # data.append(Baseline_MultiTenant_NoDPDK[l])
        # xmark.append('Baseline_MultiTenant_NoDPDK')
        data.append(Baseline_MultiTenant_DPDK[l])
        xmark.append('B')
        # data.append(SRIOV_MultiTenant_NoDPDK[l])
        # xmark.append('SRIOV_MultiTenant_NoDPDK')
        data.append(SRIOV_MultiTenant_DPDK[l])
        xmark.append('P1+\nP3')
        # data.append(SRIOV_MultiOvs_NoDPDK[l])
        # xmark.append('SRIOV_MultiOvs_NoDPDK')
        data.append(SRIOV_MultiOvs_DPDK[l])
        xmark.append('P2.1+\nP3')
        # data.append(SRIOV_MultiOvs_NoDPDK_Isolated[l])
        # xmark.append('SRIOV_MultiOvs_NoDPDK_Isolated')
        data.append(SRIOV_MultiOvs_DPDK_Isolated[l])
        xmark.append('P2.2+\nP3')
    # ax.text(6.0, 10000.05, u'64$B$')
    # ax.text(12.0, 10000.05, u'512$B$')
    # ax.text(18.0, 10000.05, u'1500$B$')
    # ax.text(23.0, 10000.05, u'2048$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=1)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 5), tuple(xmark))

    # Print median values for debug
    # medians=[]
    # for line in bp_dict['medians']:
    #    # get position data for median line
    #    x, y = line.get_xydata()[1] # top of median line
    #    # overlay median value
    #    text(x, y, '%.4f' % y,
    #         horizontalalignment='center', fontsize=5) # draw above, centered
    #    print "%.4f" % y
    #    medians.append(y)

    # plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^'))

    # plt.plot([1.0, 1.0], [-1, 10000], color='#000000')
    plt.plot([1.5, 1.5], [-1, 10000], color='#000000')
    # plt.plot([9.5, 9.5], [-1, 10000], color='#000000')
    # plt.plot([17.5, 17.5], [-1, 10000], color='#000000')
    # plt.plot([25.5, 25.5], [-1, 10000], color='#000000')
    # plt.plot([33.5, 33.5], [-1, 10000], color='#000000')
    plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,10000))
    # plt.ylabel('Latency in millisecond')
    # plt.xlabel("DPDK")

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.80])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    # plt.figtext(0.15, 0.15, 'B: Baseline', color='black')
    # plt.figtext(0.45, 0.15, 'P2.1: Principle 2 (shared cores)', color='black')
    # plt.figtext(0.15, 0.035, 'P1: Principle 1', color='black')
    # plt.figtext(0.45, 0.035, 'P2.2: Principle 2 (isolated cores)', color='black')

    ax.legend(['B: Baseline', 'P1: Principle 1', 'P2.1: Principle 2 (shared CPU)', 'P2.2: Principle 2 (isolated CPU)', 'P3: Principle 3'], handletextpad=-0.18, handlelength=0, markerscale=0, loc='lower center', ncol=3, bbox_to_anchor=(-0.315, -0.5), numpoints=1)

    # plt.add_patch(Rectangle((0, 0), 10, 10))

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-Multi-Split.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-Multi-Split.png', dpi=(250), format='png')
    plt.close()


def plotLatencyMultiSplitSingles(pcapAnalysisPath,topology):
    Baseline_MultiTenant_NoDPDK = {}
    Baseline_MultiTenant_DPDK = {}
    SRIOV_MultiTenant_NoDPDK = {}
    SRIOV_MultiTenant_DPDK = {}
    SRIOV_MultiOvs_DPDK = {}
    SRIOV_MultiOvs_NoDPDK = {}
    SRIOV_MultiOvs_NoDPDK_Isolated = {}
    SRIOV_MultiOvs_DPDK_Isolated = {}

    if topology == "phy2phy":
        Baseline_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_MultiTenant_NoDPDK-')
        Baseline_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_MultiTenant_DPDK-')
        SRIOV_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_MultiTenant_DPDK-')
        SRIOV_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_MultiTenant_NoDPDK-')
        SRIOV_MultiOvs_DPDK = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_MultiOvs_DPDK-')
        SRIOV_MultiOvs_NoDPDK = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_NoDPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_DPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2phy-latency-SRIOV_MultiOvs_DPDK-')
    elif topology == "phy2vm2vm2phy":
        Baseline_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_MultiTenant_NoDPDK-')
        Baseline_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_MultiTenant_DPDK-')
        SRIOV_MultiTenant_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_MultiTenant_DPDK-')
        SRIOV_MultiTenant_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_MultiTenant_NoDPDK-')
        SRIOV_MultiOvs_DPDK = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_MultiOvs_DPDK-')
        SRIOV_MultiOvs_NoDPDK = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_NoDPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2vm2vm2phy-latency-SRIOV_MultiOvs_NoDPDK-')
        SRIOV_MultiOvs_DPDK_Isolated = read_lat_dict(pcapAnalysisPathLatencyIsolated+'phy2vm2vm2phy-latency-SRIOV_MultiOvs_DPDK-')
    # print Baseline_MultiTenant_NoDPDK
    # print SRIOV_MultiTenant_DPDK
    # print SRIOV_MultiTenant_NoDPDK
    # print SRIOV_MultiOvs_DPDK
    # print SRIOV_MultiOvs_NoDPDK
    fig = plt.figure(1, figsize = (3.487, 2.15512978986403),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 2, 1)
    plt.tight_layout()

    c = 0

    data = []
    xmark = []
    # data.append([])
    # xmark.append("")
    c = 0
    labels = ["64bytes"]
    for l in labels:
        data.append(Baseline_MultiTenant_NoDPDK[l])
        xmark.append('Baseline')
        # data.append(Baseline_MultiTenant_DPDK[l])
        # xmark.append('Baseline_MultiTenant_DPDK')
        data.append(SRIOV_MultiTenant_NoDPDK[l])
        xmark.append('1\nvswitch\nVM')
        # data.append(SRIOV_MultiTenant_DPDK[l])
        # xmark.append('SRIOV_MultiTenant_DPDK')
        data.append(SRIOV_MultiOvs_NoDPDK[l])
        xmark.append('2\nvswitch\nVM\n(shared)')
        # data.append(SRIOV_MultiOvs_DPDK[l])
        # xmark.append('SRIOV_MultiOvs_DPDK')
        data.append(SRIOV_MultiOvs_NoDPDK_Isolated[l])
        xmark.append('2\nvswitch\nVM\n(isolated)')
        # data.append(SRIOV_MultiOvs_DPDK_Isolated[l])
        # xmark.append('SRIOV_MultiOvs_DPDK_Isolated')
    # ax.text(6.0, 10000.05, u'64$B$')
    # ax.text(12.0, 10000.05, u'512$B$')
    # ax.text(18.0, 10000.05, u'1500$B$')
    # ax.text(23.0, 10000.05, u'2048$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    colors = ['black', '#1F77B4', '#FF7F0E', '#2CA02C']
    colors = ['black']
    for color in colors:
        plt.setp(bp_dict['whiskers'], color=color, linewidth=1, linestyle='-')
        plt.setp(bp_dict['fliers'], color=color, linewidth=1, marker='+', markersize=1)
        plt.setp(bp_dict['boxes'], color=color, linewidth=1)
        plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks([1, 2, 3, 4], tuple(["B", "1", "2.1", "2.2"]))
    # plt.xticks(range(1, 5), tuple(xmark))

    plt.plot([1.5, 1.5], [-1, 10000], color='#000000')
    plt.plot([2.5, 2.5], [-1, 10000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([3.5, 3.5], [-1, 10000], color='#000000', alpha=0.1, linewidth=0.5)


    # plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,10000))
    plt.ylabel('Latency (microsecond)')

    # ax.add_patch(Rectangle((1.49, .9), 1, 10002, alpha=0.2, color='#1F77B4'))
    # ax.add_patch(Rectangle((2.49, .9), 1, 10002, alpha=0.2, color='#FF7F0E'))
    # ax.add_patch(Rectangle((3.49, .9), 1, 10002, alpha=0.2, color='#2CA02C'))


    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.80])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    ### Second plot with dpdk
    ax = plt.subplot(1, 2, 2)
    c = 0

    data = []
    xmark = []
    # data.append([])
    # xmark.append("")
    c = 0
    labels = ["64bytes"]
    for l in labels:
        # data.append(Baseline_MultiTenant_NoDPDK[l])
        # xmark.append('Baseline_MultiTenant_NoDPDK')
        data.append(Baseline_MultiTenant_DPDK[l])
        xmark.append('Baseline')
        # data.append(SRIOV_MultiTenant_NoDPDK[l])
        # xmark.append('SRIOV_MultiTenant_NoDPDK')
        data.append(SRIOV_MultiTenant_DPDK[l])
        xmark.append('1\nvswitch\nVM')
        # data.append(SRIOV_MultiOvs_NoDPDK[l])
        # xmark.append('SRIOV_MultiOvs_NoDPDK')
        data.append(SRIOV_MultiOvs_DPDK[l])
        xmark.append('2\nvswitch\nVM\n(shared CPU)')
        # data.append(SRIOV_MultiOvs_NoDPDK_Isolated[l])
        # xmark.append('SRIOV_MultiOvs_NoDPDK_Isolated')
        data.append(SRIOV_MultiOvs_DPDK_Isolated[l])
        xmark.append('2\nvswitch\nVM\n(isolated CPU)')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=1)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks([1, 2, 3, 4], tuple(["B", "1", "2.1", "2.2"]))
    # plt.xticks(range(1, 5), tuple(xmark))

    plt.plot([1.5, 1.5], [-1, 10000], color='#000000')
    plt.plot([2.5, 2.5], [-1, 10000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([3.5, 3.5], [-1, 10000], color='#000000', alpha=0.1, linewidth=0.5)

    # plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,10000))


    # ax.add_patch(Rectangle((1.49, .9), 1, 10002, alpha=0.01, color='#1F77B4'))
    # ax.add_patch(Rectangle((2.49, .9), 1, 10002, alpha=0.01, color='#FF7F0E'))
    # ax.add_patch(Rectangle((3.49, .9), 1, 10002, alpha=0.01, color='#2CA02C'))

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.80])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    plt.figtext(0.26, 0.209, "No DPDK", color="black")
    plt.figtext(0.72, 0.209, "With DPDK", color="black")


    ax.legend(['B: Baseline', '1: 1 vswitch VM', '2.1: 2 vswitch VM (shared)', '2.2: 2 vswitch VM (isolated)'], handletextpad=-0.1, handlelength=0, markerscale=0, loc='lower center', ncol=2, bbox_to_anchor=(-0.315, -0.5), numpoints=1)

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-Multi-SplitSingles.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-Multi-SplitSingles.png', dpi=(250), format='png')
    plt.close()

def read_lat_dict(path):
    # print "read_lat_dict()"
    # import ast
    ret = {}
    for i in labels:
        # print "i: " + str(i)
        ret[i] = []
        try:
            # print "printing the combo: "
            # print (str(path+i+'.res'))
            # data = ast.literal_eval(open(path+i+'.res').read())
            data = json.loads(open(path+i+'.res').read())
            # print type(data)
            # print len(data.keys())
            # continue
            for j in range(lat_packet_start_index, lat_packet_end_index):
                ret[i].append(data[unicode(str(j))] * 1000000.0) #in millisecond
                # if data[unicode(str(j))] * 1000.0 < 1:
                #     ret[i].append(data[unicode(str(j))] * 1000.0)
            print "len of ret is:" + str(len(ret[i]))
        except:
            pass

    # print ret
    return ret


# #### VISUALIZATION STUFF ####
# plotThroughputLoss(pcapAnalysisPathThroughput, topology)
# plotThroughputMultiLoss(pcapAnalysisPathThroughput, topology)
for topology in topologies:
    print "Plot the throughput"
    plotThroughputSplit(pcapAnalysisPathThroughput, topology)
    plotThroughputMultiSplit(pcapAnalysisPathThroughput, topology)
    print "Plot the latency"
    plotLatencySplitSingles(pcapAnalysisPathLatency, topology)
    plotLatencyMultiSplitSingles(pcapAnalysisPathLatency, topology)
    # break
