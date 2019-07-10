#!/usr/bin/env python
# http://matplotlib.org/api/pyplot_api.html
# https://gist.github.com/bilalhusain

import numpy as np
import matplotlib
matplotlib.use('Agg')
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
import expLib

labels = [u'44bytes', u'512bytes', u'1500bytes', u'2048bytes', u'9000bytes']
labels = [u'64bytes', u'512bytes', u'1500bytes', u'2048bytes', u'9000bytes']
lat_packet_start_index = 100
lat_packet_end_index = 10100

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
    ax.text(2.0, 10000.05, u'64$B$')
    ax.text(5.0, 10000.05, u'512$B$')
    ax.text(8.0, 10000.05, u'1500$B$')
    ax.text(11.0, 10000.05, u'2048$B$')
    ax.text(14.0, 10000.05, u'9000$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=2)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 18), tuple(xmark), rotation='-45', ha='left')

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
    plt.plot([4.5, 4.5], [-1, 10000], color='#000000')
    plt.plot([7.5, 7.5], [-1, 10000], color='#000000')
    plt.plot([10.5, 10.5], [-1, 10000], color='#000000')
    plt.plot([13.5, 13.5], [-1, 10000], color='#000000')

    plt.ylim((0.001,10000))
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

def plotLatencyMulti(pcapAnalysisPath,topology):
    Baseline_NoDPDK = {}
    Baseline_DPDK = {}
    SRIOV_NoDPDK_OneOvs = {}
    SRIOV_DPDK_OneOvs = {}
    SRIOV_NoDPDK_TwoOvs = {}
    SRIOV_DPDK_TwoOvs = {}
    SRIOV_NoDPDK_FourOvs = {}
    SRIOV_DPDK_FourOvs = {}

    if topology == "phy2phy":
        Baseline_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_NoDPDK-')
        Baseline_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_DPDK-')
        SRIOV_DPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_DPDK_OneOvs-')
        SRIOV_NoDPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_NoDPDK_OneOvs-')
        SRIOV_DPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_DPDK_TwoOvs-')
        SRIOV_NoDPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        SRIOV_DPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_DPDK_FourOvs-')
        SRIOV_NoDPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_FourOvs-')
    elif topology == "phy2vm2vm2phy":
        Baseline_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_NoDPDK-')
        Baseline_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_DPDK-')
        SRIOV_DPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_DPDK_OneOvs-')
        SRIOV_NoDPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_NoDPDK_OneOvs-')
        SRIOV_DPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_DPDK_TwoOvs-')
        SRIOV_NoDPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        SRIOV_DPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_DPDK_FourOvs-')
        SRIOV_NoDPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_FourOvs-')
    # print Baseline_NoDPDK
    # print SRIOV_DPDK_OneOvs
    # print SRIOV_NoDPDK_OneOvs
    # print SRIOV_DPDK_TwoOvs
    # print SRIOV_NoDPDK_TwoOvs
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
        data.append(Baseline_NoDPDK[l])
        xmark.append('Baseline_NoDPDK')
        data.append(Baseline_DPDK[l])
        xmark.append('baseline-dpdk')
        data.append(SRIOV_NoDPDK_OneOvs[l])
        xmark.append('SRIOV_NoDPDK_OneOvs')
        data.append(SRIOV_DPDK_OneOvs[l])
        xmark.append('SRIOV_NoDPDK_OneOvs')
        data.append(SRIOV_NoDPDK_TwoOvs[l])
        xmark.append('SRIOV_NoDPDK_TwoOvs')
        data.append(SRIOV_DPDK_TwoOvs[l])
        xmark.append('SRIOV_NoDPDK_TwoOvs')
        data.append(SRIOV_NoDPDK_FourOvs[l])
        xmark.append('SRIOV_NoDPDK_FourOvs')
        data.append(SRIOV_DPDK_FourOvs[l])
        xmark.append('SRIOV_NoDPDK_FourOvs')
    # ax.text(2.0, 10000.05, u'64$B$')
    # ax.text(7.0, 10000.05, u'512$B$')
    # ax.text(12.0, 10000.05, u'1500$B$')
    # ax.text(17.0, 10000.05, u'2048$B$')
    # ax.text(22.0, 10000.05, u'9000$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=2)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 22), tuple(xmark), rotation='-45', ha='left')

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
    # plt.plot([6.5, 4.5], [-1, 10000], color='#000000')
    # plt.plot([11.5, 7.5], [-1, 10000], color='#000000')
    # plt.plot([16.5, 10.5], [-1, 10000], color='#000000')
    # plt.plot([21.5, 13.5], [-1, 10000], color='#000000')

    plt.ylim((0.001,10000))
    plt.ylabel('Latency in millisecond')
    plt.xlabel("Scenario mode")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.78])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')
    # ax.set_xscale('log')

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-4Tenants.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-4Tenants.png', dpi=(250), format='png')
    plt.close()

def plotLatencySplit(pcapAnalysisPath,topology):
    Baseline_NoDPDK = {}
    Baseline_DPDK = {}
    SRIOV_NoDPDK_OneOvs = {}
    SRIOV_DPDK_OneOvs = {}
    SRIOV_NoDPDK_TwoOvs = {}
    SRIOV_DPDK_TwoOvs = {}
    SRIOV_NoDPDK_FourOvs = {}
    SRIOV_DPDK_FourOvs = {}

    if topology == "phy2phy":
        Baseline_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_NoDPDK-')
        Baseline_DPDK = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-Baseline_DPDK-')
        SRIOV_DPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_DPDK_OneOvs-')
        SRIOV_NoDPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2phy-latency-SRIOV_NoDPDK_OneOvs-')
        SRIOV_DPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_DPDK_TwoOvs-')
        SRIOV_NoDPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        SRIOV_DPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_DPDK_FourOvs-')
        SRIOV_NoDPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_FourOvs-')
    elif topology == "phy2vm2vm2phy":
        Baseline_NoDPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_NoDPDK-')
        Baseline_DPDK = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-Baseline_DPDK-')
        SRIOV_DPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_DPDK_OneOvs-')
        SRIOV_NoDPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'phy2vm2vm2phy-latency-SRIOV_NoDPDK_OneOvs-')
        SRIOV_DPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_DPDK_TwoOvs-')
        SRIOV_NoDPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_TwoOvs-')
        SRIOV_DPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_DPDK_FourOvs-')
        SRIOV_NoDPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_FourOvs-')
    elif topology == "vm2vm":
        Baseline_NoDPDK = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-Baseline_NoDPDK-')
        Baseline_DPDK = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-Baseline_DPDK-')
        SRIOV_DPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-SRIOV_DPDK_OneOvs-')
        SRIOV_NoDPDK_OneOvs = read_lat_dict(pcapAnalysisPath+'vm2vm-latency-SRIOV_NoDPDK_OneOvs-')
        SRIOV_DPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_DPDK_TwoOvs-')
        SRIOV_NoDPDK_TwoOvs = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_TwoOvs-')
        SRIOV_DPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_DPDK_FourOvs-')
        SRIOV_NoDPDK_FourOvs = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_FourOvs-')
    # print Baseline_NoDPDK
    # print SRIOV_DPDK_OneOvs
    # print SRIOV_NoDPDK_OneOvs
    # print SRIOV_DPDK_TwoOvs
    # print SRIOV_NoDPDK_TwoOvs
    fig = plt.figure(1, figsize = (8.75, 4.6),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 2, 1)
    plt.tight_layout()

    c = 0

    data = []
    xmark = []
    # data.append([])
    # xmark.append("")
    c = 0
    labels = ["64bytes", "512bytes", "1500bytes", "2048bytes"]
    for l in labels:
        data.append(Baseline_NoDPDK[l])
        xmark.append('Baseline')
        data.append(SRIOV_NoDPDK_OneOvs[l])
        xmark.append('1\nvswitch\nVM')
        data.append(SRIOV_NoDPDK_TwoOvs[l])
        xmark.append('2\nvswitch\nVM')
        data.append(SRIOV_NoDPDK_FourOvs[l])
        xmark.append('4\nvswitch\nVM')
    ax.text(2.0, 1000000.05, u'64$B$')
    ax.text(6.0, 1000000.05, u'512$B$')
    ax.text(10.0, 1000000.05, u'1500$B$')
    ax.text(14.0, 1000000.05, u'2048$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    colors = ['black', '#1F77B4', '#FF7F0E', '#2CA02C']
    colors = ['black']
    for color in colors:
        plt.setp(bp_dict['whiskers'], color=color, linewidth=1, linestyle='-')
        plt.setp(bp_dict['fliers'], color=color, linewidth=1, marker='+', markersize=1)
        plt.setp(bp_dict['boxes'], color=color, linewidth=1)
        plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 17), tuple(["B", "1", "2", "4", "B", "1", "2", "4", "B", "1", "2", "4", "B", "1", "2", "4"]))
    # plt.xticks(range(1, 5), tuple(xmark))

    plt.plot([1.5, 1.5], [-1, 1000000], color='#000000')
    plt.plot([2.5, 2.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([3.5, 3.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([4.5, 4.5], [-1, 1000000], color='#000000')
    plt.plot([5.5, 5.5], [-1, 1000000], color='#000000')
    plt.plot([6.5, 6.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([7.5, 7.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([8.5, 8.5], [-1, 1000000], color='#000000')
    plt.plot([9.5, 9.5], [-1, 1000000], color='#000000')
    plt.plot([10.5, 10.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([11.5, 11.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([12.5, 12.5], [-1, 1000000], color='#000000')
    plt.plot([13.5, 13.5], [-1, 1000000], color='#000000')
    plt.plot([14.5, 14.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([15.5, 15.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([16.5, 16.5], [-1, 1000000], color='#000000')


    # plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,1000000))
    plt.ylabel('Latency (microsecond)')

    # ax.add_patch(Rectangle((1.49, .9), 1, 10002, alpha=0.2, color='#1F77B4'))
    # ax.add_patch(Rectangle((2.49, .9), 1, 10002, alpha=0.2, color='#FF7F0E'))
    # ax.add_patch(Rectangle((3.49, .9), 1, 10002, alpha=0.2, color='#2CA02C'))


    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.75])
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
    labels = ["64bytes", "512bytes", "1500bytes", "2048bytes"]
    for l in labels:
        data.append(Baseline_DPDK[l])
        xmark.append('Baseline')
        data.append(SRIOV_DPDK_OneOvs[l])
        xmark.append('1\nvswitch\nVM')
        data.append(SRIOV_DPDK_TwoOvs[l])
        xmark.append('2\nvswitch\nVM')
        data.append(SRIOV_DPDK_FourOvs[l])
        xmark.append('4\nvswitch\nVM')
    ax.text(2.0, 1000000.05, u'64$B$')
    ax.text(6.0, 1000000.05, u'512$B$')
    ax.text(10.0, 1000000.05, u'1500$B$')
    ax.text(14.0, 1000000.05, u'2048$B$')

    bp_dict = plt.boxplot(data, patch_artist=False)
    plt.setp(bp_dict['whiskers'], color='black', linewidth=1, linestyle='-')
    plt.setp(bp_dict['fliers'], color='blue', linewidth=1, marker='+', markersize=1)
    plt.setp(bp_dict['boxes'], linewidth=1)
    plt.setp(bp_dict['medians'], linewidth=1, color='red')

    plt.xticks(range(1, 17), tuple(["B", "1", "2", "4", "B", "1", "2", "4", "B", "1", "2", "4", "B", "1", "2", "4"]))
    # plt.xticks(range(1, 5), tuple(xmark))

    plt.plot([1.5, 1.5], [-1, 1000000], color='#000000')
    plt.plot([2.5, 2.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([3.5, 3.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([4.5, 4.5], [-1, 1000000], color='#000000')
    plt.plot([5.5, 5.5], [-1, 1000000], color='#000000')
    plt.plot([6.5, 6.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([7.5, 7.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([8.5, 8.5], [-1, 1000000], color='#000000')
    plt.plot([9.5, 9.5], [-1, 1000000], color='#000000')
    plt.plot([10.5, 10.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([11.5, 11.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([12.5, 12.5], [-1, 1000000], color='#000000')
    plt.plot([13.5, 13.5], [-1, 1000000], color='#000000')
    plt.plot([14.5, 14.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([15.5, 15.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
    plt.plot([16.5, 16.5], [-1, 1000000], color='#000000')

    # plt.axvspan(1.5, 5.0, facecolor='0.6', alpha=0.5)

    plt.ylim((1,1000000))


    # ax.add_patch(Rectangle((1.49, .9), 1, 10002, alpha=0.01, color='#1F77B4'))
    # ax.add_patch(Rectangle((2.49, .9), 1, 10002, alpha=0.01, color='#FF7F0E'))
    # ax.add_patch(Rectangle((3.49, .9), 1, 10002, alpha=0.01, color='#2CA02C'))

    box = ax.get_position()
    ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.75])
    ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_yscale('log')

    plt.figtext(0.26, 0.209, "No DPDK", color="black")
    plt.figtext(0.72, 0.209, "With DPDK", color="black")


    # ax.legend(['B: Baseline', '1: 1 vswitch VM', '2: 2 vswitch VM', '4: 4 vswitch VM'], handletextpad=-0.1, handlelength=0, markerscale=0, loc='lower center', ncol=2, bbox_to_anchor=(-0.315, -0.5), numpoints=1)

    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-4Tenants-Split.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_box_latency_'+topology+'-4Tenants-Split.png', dpi=(250), format='png')
    plt.close()

def plotLatencyPerTenant(pcapAnalysisPath, resourceType="shared", topology="p2p",
                         throughput=10000, time=50, startOffset=10, endOffset=10,
                         tenantCount=4, packetSize="64bytes"):
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
    if resourceType == "shared":
        print "tenants" + str(tenants)
        for t in tenants:
            if topology == "p2p" or topology == "phy2phy":
                b_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-Baseline_NoDPDK-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                o_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_OneOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                t_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_TwoOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                f_tLat_p2p[t] = read_lat_dict(pcapAnalysisPath + 'phy2phy-latency-SRIOV_NoDPDK_FourOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
            elif topology == "p2v" or topology == "phy2vm2vm2phy":
                b_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-Baseline_NoDPDK-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                o_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_OneOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                t_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_TwoOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                f_tLat_p2v[t] = read_lat_dict(pcapAnalysisPath + 'phy2vm2vm2phy-latency-SRIOV_NoDPDK_FourOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
            elif topology == "v2v" or topology == "vm2vm":
                if t == "tenant3" or t == "tenant4":
                    continue
                else:
                    b_tLat_v2v[t] = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-Baseline_NoDPDK-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                    o_tLat_v2v[t] = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_OneOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
                    t_tLat_v2v[t] = read_lat_dict(pcapAnalysisPath + 'vm2vm-latency-SRIOV_NoDPDK_TwoOvs-', True, t,
                                              topo=topology, throughput=throughput, time=time, startOffset=startOffset,
                                              endOffset=endOffset, tenantCount=tenantCount)
    # pprint.pprint(two_tLat_p2p[tenants[0]]["64bytes"])

    fig = plt.figure(1, figsize = (8.75, 4.6),frameon=True)
    fig.autofmt_xdate(bottom=0.1, rotation=90, ha='right')
    ax = plt.subplot(1, 1, 1)
    # plt.tight_layout()
    c = 0

    data = []
    xmark = []
    c = 0
    if topology == "p2p" or topology == "phy2phy":
        for t in tenants:
            data.append(b_tLat_p2p[t][packetSize])
        for t in tenants:
            data.append(o_tLat_p2p[t][packetSize])
        for t in tenants:
            data.append(t_tLat_p2p[t][packetSize])
        for t in tenants:
            data.append(f_tLat_p2p[t][packetSize])
    elif topology == "p2v" or topology == "phy2vm2vm2phy":
        for t in tenants:
            data.append(b_tLat_p2v[t][packetSize])
        for t in tenants:
            data.append(o_tLat_p2v[t][packetSize])
        for t in tenants:
            data.append(t_tLat_p2v[t][packetSize])
        for t in tenants:
            data.append(f_tLat_p2v[t][packetSize])
    elif topology == "v2v" or topology == "vm2vm":
        for t in ["tenant1", "tenant2"]:
            data.append(b_tLat_v2v[t][packetSize])
        for t in ["tenant1", "tenant2"]:
            data.append(o_tLat_v2v[t][packetSize])
        for t in ["tenant1", "tenant2"]:
            data.append(t_tLat_v2v[t][packetSize])
    # pprint.pprint(data)
    print "len(data): " + str(len(data))

    plotType = "boxplot"
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

        plt.xticks(range(1, 17),
                   tuple(["B-T1", "B-T2", "B-T3", "B-T4", "1-T1", "1-T2", "1-T3", "1-T4",
                          "2-T1", "2-T2", "2-T3", "2-T4", "4-T1", "4-T2", "4-T3", "4-T4"]))
        # plt.xticks(range(1, 5), tuple(xmark))

        # plt.plot([1.5, 1.5], [-1, 1000000], color='#000000')
        # plt.plot([2.5, 2.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        # plt.plot([3.5, 3.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        plt.plot([4.5, 4.5], [-1, 1000000], color='#000000')
        # plt.plot([5.5, 5.5], [-1, 1000000], color='#000000')
        # plt.plot([6.5, 6.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        # plt.plot([7.5, 7.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        plt.plot([8.5, 8.5], [-1, 1000000], color='#000000')
        # plt.plot([9.5, 9.5], [-1, 1000000], color='#000000')
        # plt.plot([10.5, 10.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        # plt.plot([11.5, 11.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        plt.plot([12.5, 12.5], [-1, 1000000], color='#000000')
        # plt.plot([13.5, 13.5], [-1, 1000000], color='#000000')
        # plt.plot([14.5, 14.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        # plt.plot([15.5, 15.5], [-1, 1000000], color='#000000', alpha=0.1, linewidth=0.5)
        # plt.plot([16.5, 16.5], [-1, 1000000], color='#000000')

        plt.ylim((1,10000))
        plt.ylabel('Latency ($\mu$s)')
        # box = ax.get_position()
        # ax.set_position([box.x0 + 0.05, box.y0 + box.height * 0.25, box.width * 0.91, box.height * 0.75])
        ax.yaxis.grid(True, linestyle='-', which='major', color='grey', alpha=0.8)
        ax.set_axisbelow(True)
        ax.set_yscale('log')

    plt.title("Per tenant latency analysis for "+topology+ "@" + str(throughput) + "pps" + " for " + packetSize + " packets")
    figureName = "plot_lat_pertenant_"+plotType+"_"+resourceType+"_"+topology+"_"+str(throughput)+"pps"+"_"+packetSize+".png"
    plt.savefig(pcapAnalysisPath + figureName)
    return figureName

def read_lat_dict(path, isTenant=False, tenant="tenant1", topo="p2p",
                  throughput=10000, time=50, startOffset=10, endOffset=10,
                  tenantCount=4):
    # print "read_lat_dict()"
    # import ast
    tenantTput = throughput/tenantCount
    startIndex = tenantTput*startOffset
    ret = {}
    for i in labels:
        # print "i: " + str(i)
        ret[i] = []
        try:
            # print "printing the combo: "
            # print (str(path+i+'.res'))
            # data = ast.literal_eval(open(path+i+'.res').read())
            if isTenant is False:
                data = json.loads(open(path+i+'.res').read())
            else:
                data = json.loads(open(path+i+'-'+tenant+'.res').read())
            # continue
            if isTenant is False:
                for j in range(0, len(data.keys())):
                    ret[i].append(data[unicode(str(j))] * 1000000.0) #in microsecond
                    # if data[unicode(str(j))] * 1000.0 < 1:
                    #     ret[i].append(data[unicode(str(j))] * 1000.0)
            elif isTenant is True:
                if topo != "v2v":
                    print "len(data.keys(): " + str(len(data.keys()))
                    # for j in range(2500, 2500+len(data.keys())-5):
                    for j in range(startIndex, startIndex + len(data.keys()) - 5):
                        if data[unicode(str(j))] * 1000000.0 > 1000000:
                            print str(j) + " has latency greater than 1 second!!" + str(data[unicode(str(j))] * 1000000.0)
                        else:
                            ret[i].append(data[unicode(str(j))] * 1000000.0) #in microsecond
                elif topo == "v2v":
                    for j in range(startIndex, startIndex + len(data.keys())):
                        if data[unicode(str(j))] * 1000000.0 > 1000000:
                            print str(j) + " has latency greater than 1 second!!"
                        else:
                            ret[i].append(data[unicode(str(j))] * 1000000.0) #in microsecond
            print "len of ret is:" + str(len(ret[i]))
        except Exception as e:
            print (e)

    # print ret
    return ret

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

    plt.plot(baseline_noDpdk_tx, baseline_noDpdk_rx, marker=marker.next(), color='#79c36a', linestyle='', label='baseline_nodpdk', markersize=9)
    plt.plot(baseline_Dpdk_tx, baseline_Dpdk_rx, marker=marker.next(), color='#79c36a', linestyle='', label='baseline_dpdk', markersize=9)
    plt.plot(sriov_noDpdk_tx, sriov_noDpdk_rx, marker=marker.next(), color='#599ad3', linestyle='', label='sriov_nodpdk', markersize=9)
    plt.plot(sriov_dpdk_tx, sriov_dpdk_rx, marker=marker.next(), color='#727272', linestyle='', label='sriov_dpdk', markersize=9)

    # plt.ylim((300000, 700000 + 20000))
    # plt.xlim((300000, 1500000 + 20000))
    plt.ylabel('Packets/s Forwarded')
    plt.xlabel("Packets/s Sent")

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
    SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx = [], []
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
    print Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx
    print SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx
    print SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx
    print SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx
    print SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx
    fig = plt.figure(1, figsize=(8.75, 4.6), frameon=True)
    ax = plt.subplot(111)

    plt.grid(True)
    marker = itertools.cycle(('d', '*', 'o', '^', 'p'))

    plt.plot(Baseline_MultiTenant_NoDPDK_tx, Baseline_MultiTenant_NoDPDK_rx, marker=marker.next(), color='#79c36a', linestyle='', label='Baseline_MultiTenant_NoDPDK', markersize=9)
    plt.plot(Baseline_MultiTenant_DPDK_tx, Baseline_MultiTenant_DPDK_rx, marker=marker.next(), color='#727272', linestyle='', label='Baseline_MultiTenant_DPDK', markersize=9)
    plt.plot(SRIOV_MultiTenant_DPDK_tx, SRIOV_MultiTenant_DPDK_rx, marker=marker.next(), color='#599ad3', linestyle='', label='SRIOV_MultiTenant_DPDK', markersize=9)
    plt.plot(SRIOV_MultiTenant_NoDPDK_tx, SRIOV_MultiTenant_NoDPDK_rx, marker=marker.next(), color='#727272', linestyle='', label='SRIOV_MultiTenant_NoDPDK', markersize=9)
    plt.plot(SRIOV_MultiOvs_DPDK_tx, SRIOV_MultiOvs_DPDK_rx, marker=marker.next(), color='#599ad3', linestyle='',
             label='SRIOV_MultiOvs_DPDK', markersize=9)
    plt.plot(SRIOV_MultiOvs_NoDPDK_tx, SRIOV_MultiOvs_NoDPDK_rx, marker=marker.next(), color='#727272',
             linestyle='', label='SRIOV_MultiOvs_NoDPDK', markersize=9)


    # plt.ylim((300000, 1400000 + 20000))
    # plt.xlim((300000, 1400000 + 20000))
    plt.ylabel('Packets/s Forwarded (k pps)')
    plt.xlabel("Packets/s Sent (k pps)")

    ax.legend(loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.45), numpoints=1)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25, box.width * 1.0, box.height * 0.75])
    ax.set_axisbelow(True)

    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi.pdf', dpi=(2500), format='pdf')
    plt.savefig(pcapAnalysisPath+'plot_tput_'+topology+'-Multi.png', dpi=(320), format='png')
    plt.close()

def tabulateTput(pcapAnalysisPath, topology, vswitchMode, isIsolated, txrxFiles, txThroughput):
    print "tabulateTput()"
    import os.path
    import csv
    if os.path.isfile(pcapAnalysisPath+"tput.csv") is False:
        print "create the tput table csv file."
        headings = ["topology", "vswitchMode", "isIsolated", "tx (Mpps)", "rx (Mpps)"]
        with open(pcapAnalysisPath+"tput.csv", 'a') as tputFile:
            wr = csv.writer(tputFile, quoting=csv.QUOTE_NONE)
            wr.writerow(headings)
    else:
        print "tput table csv already exits. Will append data."
    if len(txrxFiles) == 1:
        txTput = txThroughput * 1.0 / 1000000
        rx = pcapAnalysisPath + txrxFiles[0]
        rxTput = parse_tput_dict_dagbits(rx)
    elif len(txrxFiles) == 2:
        tx = pcapAnalysisPath + txrxFiles[0]
        rx = pcapAnalysisPath + txrxFiles[1]
        txTput = parse_tput_dict_dagbits(tx)
        rxTput = parse_tput_dict_dagbits(rx)
    data = [topology, vswitchMode, isIsolated, txTput, rxTput]
    with open(pcapAnalysisPath+"tput.csv", 'a') as tputFile:
        wr = csv.writer(tputFile, quoting=csv.QUOTE_NONE)
        wr.writerow(data)

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

def parse_tput_dict(dict_data):
    try:
        for l in open(dict_data):
            if l.split()[0] == 'Average':
                return int(float(l.split()[3])/1000)
    except:
        print "Looks like its empty!"
        return 0
def parse_tput_dict_dagbits(tputFile):
    try:
        foundRate = False
        for l in open(tputFile):
            if l.split(':')[0] == '    Rate' and foundRate is False:
                foundRate = True
            if l.split(':')[0] == '    Rate' and foundRate is True:
                rateLine = l.split(':')
                rate = rateLine[1].split('(')[1].split()[0]
                return float(float(rate)/1000000.0)
    except:
        print "Looks like its empty!"
        return 0
