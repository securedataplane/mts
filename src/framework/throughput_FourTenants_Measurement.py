#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A SCRIPT TO MEASURE THE ONE-WAY FORWARDING THROUGHPUT OF SEVERAL TRAFFIC
SCENARIOS, VSWITCH MODES AND CPU ALLOCATIONS. THE DATA COLLECTED FOR THE ATC'19
PAPER WAS BASED ON THIS SCRIPT.
"""

from packetOperator import *
from expLib import *
from prepTestbed import *
from visualization.visualizer import *

from datetime import datetime
import pprint

logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
emailPlots = True # Email plots. Requires credentials in expLib
packetCaptureTool = "dagbits" # Which packet capture tool to use
throughputTestTime = 110 # Time to transmit packets
monitor = cnx_dosse # Server on which the (tx and rx) packets are captured
store = cnx_spree # Server for storage and plotting
tenants = [cnx_Ptenant1, cnx_Ptenant2, cnx_Ptenant3, cnx_Ptenant4] # Tenant VMs

'''
@topology is the traffic scenario
@vswitchMode is the vswitch mode
@isolateCPUs True/False indicates whether the vswitch vms have isolated cores or
not respectively
@vswitchCores The number of cores for vswitching
'''
def throughput(topology="phy2phy", vswitchMode="Baseline_NoDPDK", isolateCPUs=False, vswitchCores=1):
    ############################################################################
    # Three different throughput lists (ratesLow, ratesMid and ratesHig) are
    # created and finally merged into throughputRates.
    ############################################################################
    throughputRates = [] # List of throughput rates to test
    ratesLow = range(14000000, 15000000, 1000000)

    ############################################################################
    # A few exceptions when running the Baseline mode as 14 Mpps overwhelmed our
    # system and prevented the vswitch from reaching its max. throughput
    ############################################################################
    if vswitchMode == "Baseline_NoDPDK":
        if topology == "phy2vm2vm2phy" or topology == "vm2vm":
            ratesLow = range(500000, 600000, 100000)
    ratesMid = None
    ratesHigh = None
    ratesAll = [ratesLow, ratesMid, ratesHigh]
    for rates in ratesAll:
        if rates is not None:
            throughputRates.extend(rates)
    print("[*] Using following throughputRates")
    print(throughputRates)
    txDirectionHosts = "dosseplane" # For the filenames and id traffic direction
    rxDirectionHosts = "planedosse" # For the filenames and id traffic direction
    txInterface = "dag0:6" # The interface that transmits the packets
    rxInterface = "dag0:2" # The interface that receives the forwarded packets
    trial = 0 # Number of trials/repetitions
    print("[*] Going to test the foll. throughput rates: " + str(throughputRates))
    print("[*] Going to test the foll.:" + topology + ", " + vswitchMode)
    print("[*] Create log directory")
    experiment = "throughput"

    # Create a unique directory on disk to save data, e.g., files.
    pcapDataPath = preparePcapDataPath(monitor, logTimeStamp, experiment, topology, vswitchMode, isolateCPUs)

    # Create a unique directory on disk to save analyzed data, e.g., parsed data
    pcapAnalysisPath = preparePcapAnalysisPath(monitor, logTimeStamp, experiment, isolateCPUs)

    # Make sure the monitor is not already capturing data
    cleanUpPacketOperators(cnx=monitor)

    # Collect measurement data for the different throughput rates
    for throughput in throughputRates:
        print("Sleep 20s before starting packet capture to avoid capturing multicast packets.")
        time.sleep(20)

        ########################################################################
        # dagbits is used for throughput measurements as we simply monitor
        # the received throughput, the packets themselves are not
        # interesting.
        # if using tcpdump we capture the packets and then compute the
        # throughput on the pcaps.
        ########################################################################
        if packetCaptureTool == "dagbits":
            txCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + txDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".txt"
            rxCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + rxDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".txt"
        elif packetCaptureTool == "tcpdump":
            txCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + txDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
            rxCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + rxDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
        trafficFile = "" # the file name that contains packets to be replayed
        trafficPath = "/root/replay/single-multi-tenant/" # the path to it

        ########################################################################
        # The packet file names are created based on the vswitch mode and the
        # traffic scenario/topology, hence we have to set trafficFile
        # accordingly.
        ########################################################################
        if topology == "phy2vm2vm2phy" or topology == "phy2phy":
            if vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "Baseline_NoDPDK" or\
                    vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "Baseline_DPDK":
                trafficFile = "SingleOvsVm-4tenants-throughput-7.5Mpps-64bytes-port0-10s.erf"
            elif vswitchMode == "SRIOV_NoDPDK_TwoOvs" or vswitchMode == "SRIOV_DPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-throughput-7.5Mpps-64bytes-port0-10s.erf"
            elif vswitchMode == "SRIOV_NoDPDK_FourOvs" or vswitchMode == "SRIOV_DPDK_FourOvs":
                trafficFile = "FourOvsVm-4tenants-throughput-7.5Mpps-64bytes-port0-10s.erf"
            if trafficFile == "":
                print("Could not set the traffic file!")
                break
        elif topology == "vm2vm":
            if vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "Baseline_NoDPDK" or\
                    vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "Baseline_DPDK":
                trafficFile = "SingleOvsVm-4tenants-VMVM-throughput-7.5Mpps-64bytes-port0-10s.erf"
            elif vswitchMode == "SRIOV_NoDPDK_TwoOvs" or vswitchMode == "SRIOV_DPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-VMVM-throughput-7.5Mpps-64bytes-port0-10s.erf"
            if trafficFile == "":
                print("Could not set the traffic file!")
                break

        ########################################################################
        # Measurements are now ready to be made.
        # When using dagbits, we first start the packet generator as it takes
        # about 10 seconds to ramp up to 14 Mpps. Hence, we sleep for 10s and
        # then start capturing packets.
        ########################################################################
        if packetCaptureTool == "dagbits":
            print("Starting measurement! The time is: " + str(datetime.now()))
            print("Starting packet gen.")
            startEndacePktGen(cnx=monitor, throughput=str(throughput), loop=210, trafficFile=trafficFile, limitTime=True, time=throughputTestTime,
                              packet_replay_path=trafficPath, background=True)
            print("Start packet capture in 10s")
            time.sleep(10)

            ####################################################################
            # Capture packets on the tx and rx interfaces. However, using the
            # Endace 10x4P without a solid state drive cannot handle 14 Mpps on
            # two interfaces, hence, it can suffice to measure the throughput on
            # only the interface (rx) that receives the forwarded packets.
            ####################################################################
            startPacketCapture(cnx=monitor,interface=txInterface,fileName=txCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision="micro", tool="dagbits")
            startPacketCapture(cnx=monitor,interface=rxInterface,fileName=rxCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision="micro", tool="dagbits")
            print("Now sleep for " + str(throughputTestTime) + ", so that packet gen and capture have completed")
            time.sleep(throughputTestTime)
        print("Finished transmitting packets.")
        print("Now stop the packet capture")
        stopPacketCapture(cnx=monitor)

        # Throughput Computation (Current limitation: cannot run computeThroughput() on nanosecond pcap files)
        print("Now compute the throughput")
        computeThroughput(monitor, pcapDataPath,
                          [rxCaptureFileName],
                          pcapAnalysisPath, topology, vswitchMode,
                          throughput, packetCaptureTool=packetCaptureTool)

        # scp the data to a data storage system
        print("scp the files to plot")
        if packetCaptureTool == "dagbits":
            scp(monitor, store, pcapAnalysisPath, ["*-throughput-*-0.txt"], pcapAnalysisPath)
        else:
            scp(monitor, store, pcapAnalysisPath, ["*-throughput-*-0.pcap"], pcapAnalysisPath)

        # Tabulate the data in csv format
        tabulateTput(pcapAnalysisPath, topology, vswitchMode, isolateCPUs, [rxCaptureFileName], throughput)

        ########################################################################
        # If using tcpdump, to save disk space the pcaps can be compressed using
        # pigz which may need to be installed if not already available
        ########################################################################
        if packetCaptureTool == "tcpdump":
            print("Now compress pcaps")
            print("Pcap files are now compressed: ")
            if compressPcapFiles(monitor, pcapDataPath, [txCaptureFileName, rxCaptureFileName]) is True:
                print("Remove the pcap files")
                removePcapFiles(monitor, pcapDataPath, [txCaptureFileName, rxCaptureFileName])

        print("Cleanup packetOperators: dagflood, " + packetCaptureTool)
        cleanUpPacketOperators(monitor)

        if emailPlots is True:
            attachmentFileName="tput.csv"
            print("Now email the plots")
            EmailNotify("Throughput setup is " + str(topology) + ", " +
                        str(vswitchMode) + ", " + str(isolateCPUs) +
                        ". Summary for "+topology+" single tenant throughput attached: " + str(datetime.now()),
                        ": Throughput measurement done.",
                        datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                        attachmentPath=pcapAnalysisPath + attachmentFileName)

def main():
    topologies = ["phy2phy", "phy2vm2vm2phy", "vm2vm"]
    # all the different vswitch modes
    vswitchModes = ["SRIOV_NoDPDK_OneOvs",
                    "SRIOV_NoDPDK_TwoOvs",
                    "SRIOV_NoDPDK_FourOvs",
                    "Baseline_NoDPDK",
                    "Baseline_NoDPDK_2Core",
                    "Baseline_NoDPDK_4Core",
                    "SRIOV_DPDK_OneOvs",
                    "SRIOV_DPDK_TwoOvs",
                    "SRIOV_DPDK_FourOvs",
                    "Baseline_DPDK",
                    "Baseline_DPDK_2Core",
                    "Baseline_DPDK_4Core"]

    # The server running the vswitch
    dut = cnx_havel
    # If the system should isolate the vswitch vm cores or not
    isCPUIsolated = [False, True]

    print("[*] topologies: " + str(topologies))
    print("[*] vswitchModes: " + str(vswitchModes))
    print("[*] isCPUIsolated: " + str(isCPUIsolated))
    print("[*] dut: " + str(dut))

    exp_start_time = datetime.now()
    print("[*] Script started at: " + str(logTimeStamp))

    ############################################################################
    # Throughput measurement methodology
    # [1] Iterate through each of the following.
    # 	* cpu isolation mode
    # 	* topology
    # 	* vswitch mode
    # [2] Prepare the server accordingly
    # [3] If that was successful, start the measurements
    # [4] If emails are enabled, send an email after a throughput measurement
    #     has completed.
    # [5] Repeat till all configuration permutations are done.
    ############################################################################
    for cpuIsolation in isCPUIsolated:
        for topology in topologies:
            for vswitchMode in vswitchModes:
                vswitchCore = getNbrCores(vswitchMode, cpuIsolation)
                print("[*] vswitchCore: " + str(vswitchCore))
                ################################################################
                # Next prepare the server, e.g., allocate cores, set-up the
                # vswitch vms, run the l2fwd apps in the tenant vms
                ################################################################
                result = prepTestbed(dut, topology, vswitchMode, isolateCPUs=cpuIsolation, vswitchCores=vswitchCore)
                if result is True:
                    start = datetime.now()
                    if emailPlots is True:
                        EmailNotify("Throughput setup is" + str(dut) + ", " + str(topology) + ", " +
                                        str(vswitchMode) + ", " + str(cpuIsolation),
                                        ": Throughput measurements going to start now.",
                                        start.strftime("%Y-%m-%d_%H-%M-%S"))
                    throughput(topology=topology, vswitchMode=vswitchMode,
                               isolateCPUs=cpuIsolation, vswitchCores=vswitchCore)
                    if emailPlots is True:
                        EmailNotify("Throughput setup is" + str(dut) + ", " + str(topology) + ", " +
                                        str(vswitchMode) + ", " + str(cpuIsolation) +
                                        "Time to test throughput is: " + str(datetime.now() - start),
                                        ": Throughput measurement done.",
                                        datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                    print("Time to test throughput is: " + str(datetime.now() - start))
        print("Total experiment run time is: " + str(datetime.now() - exp_start_time))

if __name__ == "__main__":
    main()

