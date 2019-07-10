#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 13:20 2019

@author: Kashyap Thimmaraju
@email: kashyap.thimmaraju@sect.tu-berlin.de
"""

from packetOperator import *
from expLib import *
from prepTestbed import *
from visualizer import *

from datetime import datetime
import pprint

logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def main():
    # topologies p2p=phy2phy, p2v=phy2vm2vm2phy, v2v=vm2vm
    # For the moment don't use v2v
    topologies = ["phy2phy", "phy2vm2vm2phy", "vm2vm"]
    # vswitchModes = SRIOV with/without DPDK and no. of vswitch vms
    # Your servers won't work with Baseline_DPDK atm
    vswitchModes = ["SRIOV_NoDPDK_OneOvs",
                    "SRIOV_NoDPDK_TwoOvs",
                    "SRIOV_NoDPDK_FourOvs",
                    "Baseline_NoDPDK",
                    "SRIOV_DPDK_OneOvs",
                    "SRIOV_DPDK_TwoOvs",
                    "SRIOV_DPDK_FourOvs"]
    # dut = cnx_plane (for abhiraj) or cnx_havel (for lukas)
    dut = cnx_plane
    # isCPUIsolated for the vswitch vms
    # can't use False && SRIOV_NoDPDK_OneOvs
    # can't use False && Baseline_NoDPDK
    isCPUIsolated = [False, True]

    print "topologies: " + str(topologies)
    print "vswitchModes: " + str(vswitchModes)
    print "isCPUIsolated: " + str(isCPUIsolated)
    print "dut: " + str(dut)

    exp_start_time = datetime.now()
    print "Script started at: " + str(logTimeStamp)

    # Iterate over the list of factors (topologies, vswitchModes, cpuIsolation)
    # If you want to run just one, make sure the lists have only 1 element each.
    for cpuIsolation in isCPUIsolated:
        for topology in topologies:
            for vswitchMode in vswitchModes:
                vswitchCore = getNbrCores(vswitchMode, cpuIsolation)
                print "vswitchCore: " + str(vswitchCore)
                result = prepTestbed(dut, topology, vswitchMode, isolateCPUs=cpuIsolation, vswitchCores=vswitchCore)
        print "Total experiment run time is: " + str(datetime.now() - exp_start_time)

if __name__ == "__main__":
    main()
