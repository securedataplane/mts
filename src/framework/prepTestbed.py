# -*- coding: utf-8 -*-
"""
Created on Tue Nov 9 10:15 2018

@author: Kashyap Thimmaraju
@email: kashyap.thimmaraju@sect.tu-berlin.de
"""

'''
Functions to configure the servers for the desired traffic scenario/topology,
vswitch mode and resource allocation.

The specific configuration for each
permutation is specified in another library, e.g., FourTenantLib or
ContainerLib.

The specific library to use needs to be programmed here depending
on the vswitch mode.
* VM vswitch modes are handled in the FourTenantLib and vm2vmLib for the p2p,
  p2v and vm2vm traffic scenarios respectively.
* Container vswitch modes are handled in the ContainerLib.

For allocating cores to the vswitch compartment
getNbrCores needs to be programmed to return the number of cores for the desired
vswitch mode.
* Note that for Baseline_DPDK* vswitch modes, the number of cores allocated is
  one more than mentioned in the vswitch mode as the Host OS gets one core and
  the other cores are allocated for dpdk polling. Hence, e.g.,
  Baseline_DPDK_4Core is returns 5 cores, where 1 is for the Host OS and the
  remaining 4 are for DPDK polling.
'''

import FourTenantLib as ftl
import ContainerLib as cl
import vm2vmLib as vm2vm
from datetime import datetime

# containerConfig=[numVMs, numCont, numTenants]
def prepTestbed(cnx, topology, vswitchMode, isolateCPUs=True, vswitchCores=1, containerConfig=[]):
    print "prepTestbed" + "topology: " + topology + ", vswitchMode: " + vswitchMode + ", isolateCPUs: " + str(isolateCPUs)
    if topology == "phy2phy":
        if vswitchMode == "Baseline_NoDPDK" and isolateCPUs is False:
            start = datetime.now()
            result = ftl.phy2phy_Baseline(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "Baseline_NoDPDK_2Core" or vswitchMode == "Baseline_NoDPDK_4Core" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2phy_Baseline(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "Baseline_DPDK" or vswitchMode == "Baseline_DPDK_2Core" or \
                vswitchMode == "Baseline_DPDK_4Core" and isolateCPUs is True:
            # print "Currently unavailable!"
            # result = False
            start = datetime.now()
            result = ftl.phy2phy_Baseline(cnx, isDPDK=True, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs" and isolateCPUs is False:
            start = datetime.now()
            result = ftl.phy2phy_SRIOV_OneOvs(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs_Container" and isolateCPUs is False:
            start = datetime.now()
            result = cl.phy2phy_SRIOV_Dynamic_Container(cnx, isDPDK=False, nbrCores=vswitchCores, numVMs=1, numCont=1)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_Dynamic_Container" and isolateCPUs is False:
            start = datetime.now()
            result = cl.phy2phy_SRIOV_Dynamic_Container(cnx, isDPDK=False, nbrCores=vswitchCores, numVMs=containerConfig[0], numCont=containerConfig[1], numTenants=containerConfig[2])
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_OneOvs" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2phy_SRIOV_OneOvs(cnx, isDPDK=True, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
            start = datetime.now()
            result = ftl.phy2phy_SRIOV_TwoOvs(cnx, isDPDK=False, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_TwoOvs" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2phy_SRIOV_TwoOvs(cnx, isDPDK=True, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_FourOvs":
            start = datetime.now()
            result = ftl.phy2phy_SRIOV_FourOvs(cnx, isDPDK=False, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_FourOvs" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2phy_SRIOV_FourOvs(cnx, isDPDK=True, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        else:
            print "Baseline and SRIOV_*_OneOvs get one core; DPDK is always isolated; so run just once."
            return False

    #################################################################
    elif topology == "phy2vm2vm2phy":
        if vswitchMode == "Baseline_NoDPDK" and isolateCPUs is False:
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_Baseline(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "Baseline_NoDPDK_2Core" or vswitchMode == "Baseline_NoDPDK_4Core" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_Baseline(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "phy2vm2vm2phy_Baseline_DPDK" and isolateCPUs is True:
            # print "Currently unavailable!"
            # result = False
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_Baseline(cnx, isDPDK=True, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs" and isolateCPUs is False:
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_SRIOV_OneOvs(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs_Container" and isolateCPUs is False:
            start = datetime.now()
            result = cl.phy2vm2vm2phy_SRIOV_Dynamic_Container(cnx, isDPDK=False, nbrCores=vswitchCores, numVMs=1, numCont=1)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_Dynamic_Container" and isolateCPUs is False:
            start = datetime.now()
            result = cl.phy2vm2vm2phy_SRIOV_Dynamic_Container(cnx, isDPDK=False, nbrCores=vswitchCores, isIsolated=False, numVMs=containerConfig[0], numCont=containerConfig[1], numTenants=containerConfig[2])
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_OneOvs" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_SRIOV_OneOvs(cnx, isDPDK=True, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_SRIOV_TwoOvs(cnx, isDPDK=False, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_TwoOvs" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_SRIOV_TwoOvs(cnx, isDPDK=True, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_FourOvs":
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_SRIOV_FourOvs(cnx, isDPDK=False, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_FourOvs" and isolateCPUs is True:
            start = datetime.now()
            result = ftl.phy2vm2vm2phy_SRIOV_FourOvs(cnx, isDPDK=True, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        else:
            print "Baseline and SRIOV_*_OneOvs get one core; DPDK is always isolated; so run just once."
            return False
        #################################################################
    elif topology == "vm2vm":
        if vswitchMode == "Baseline_NoDPDK" and isolateCPUs is False:
            start = datetime.now()
            result = vm2vm.vm2vm_Baseline(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "Baseline_NoDPDK_2Core" or vswitchMode == "Baseline_NoDPDK_4Core" and isolateCPUs is True:
            start = datetime.now()
            result = vm2vm.vm2vm_Baseline(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "Baseline_DPDK" and isolateCPUs is True:
            # print "Currently unavailable!"
            # result = False
            start = datetime.now()
            result = vm2vm.vm2vm_Baseline(cnx, isDPDK=True, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs" and isolateCPUs is False:
            start = datetime.now()
            result = vm2vm.vm2vm_SRIOV_OneOvs(cnx, isDPDK=False, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_OneOvs" and isolateCPUs is True:
            start = datetime.now()
            result = vm2vm.vm2vm_SRIOV_OneOvs(cnx, isDPDK=True, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
            start = datetime.now()
            result = vm2vm.vm2vm_SRIOV_TwoOvs(cnx, isDPDK=False, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_DPDK_TwoOvs" and isolateCPUs is True:
            start = datetime.now()
            result = vm2vm.vm2vm_SRIOV_TwoOvs(cnx, isDPDK=True, isIsolated=isolateCPUs, nbrCores=vswitchCores)
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "Could not prepare testbed, move to the next one."
        elif vswitchMode == "SRIOV_NoDPDK_FourOvs":
            start = datetime.now()
            result = False
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "No FourOvs scenario for vm2vm."
        elif vswitchMode == "SRIOV_DPDK_FourOvs" and isolateCPUs is True:
            start = datetime.now()
            result = False
            print "Time to init testbed is: " + str(datetime.now() - start)
            if result is True:
                return True
            else:
                print "No FourOvs scenario for vm2vm."
        else:
            print "Baseline and SRIOV_*_OneOvs get one core; DPDK is always isolated; so run just once."
            return False

        #################################################################

def getNbrCores(vswitchMode="Baseline_NoDPDK", cpuIsolation=False):
    print "getNbrCores()"
    if cpuIsolation is False:
        print "cpuIsolation False:"
        if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "SRIOV_NoDPDK_OneOvs_Container" or\
            vswitchMode == "SRIOV_NoDPDK_Dynamic_Container" or vswitchMode == "SRIOV_NoDPDK_TwoOvs" or vswitchMode == "SRIOV_NoDPDK_FourOvs":
            # print "1 core for shared and NoDPDK vswitchMode"
            return 1
        elif vswitchMode == "Baseline_DPDK" or \
                vswitchMode == "SRIOV_DPDK_OneOvs" or \
                vswitchMode == "SRIOV_DPDK_TwoOvs" or \
                vswitchMode == "SRIOV_DPDK_FourOvs" or \
                vswitchMode == "Baseline_NoDPDK_2Cores" or \
                vswitchMode == "Baseline_NoDPDK_4Cores":
            print "No DPDK, Baseline_NoDPDK_2Cores and Baseline_NoDPDK_4Cores when cpuIsolation is False."
        else:
            print "Unknown vswitchMode"
            exit()
    elif cpuIsolation is True:
        print "cpuIsolation True:"
        if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "Baseline_DPDK":
            return 1
        elif vswitchMode == "Baseline_NoDPDK_2Core":
            return 2
        elif vswitchMode == "Baseline_DPDK_2Core":
            return 3
        elif vswitchMode == "Baseline_NoDPDK_4Core":
            return 4
        elif vswitchMode == "Baseline_DPDK_4Core":
            return 5
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "SRIOV_NoDPDK_OneOvs_Container":
            return 1
        elif vswitchMode == "SRIOV_NoDPDK_TwoOvs" or vswitchMode == "SRIOV_DPDK_TwoOvs":
            return 1
        elif vswitchMode == "SRIOV_NoDPDK_FourOvs" or vswitchMode == "SRIOV_DPDK_FourOvs":
            return 1
        else:
            print "Unknown vswitchMode"
            exit()
