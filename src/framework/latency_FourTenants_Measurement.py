#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A SCRIPT TO MEASURE THE ONE-WAY FORWARDING LATENCY OF SEVERAL TRAFFIC
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
packetCaptureTool = "dagsnap" # Which packet capture tool to use
throughputTestTime = 30 # Time to transmit packets
monitor = cnx_dosse # Server on which the (tx and rx) packets are captured
store = cnx_spree # Server for storage and plotting
tsPrecision = "micro" # time stamp precision: micro or nano
startOffset = 10 # in seconds to skip from the start of captured packets
endOffset = 10 # in seconds to skip from the end of captured packets
tenants = [cnx_Ptenant1, cnx_Ptenant2, cnx_Ptenant3, cnx_Ptenant4]

'''
@topology is the traffic scenario
@vswitchMode is the vswitch mode
@isolateCPUs True/False indicates whether the vswitch vms have isolated cores or
not respectively
@vswitchCores The number of cores for vswitching
'''
def latency(topology="phy2phy", vswitchMode="Baseline_NoDPDK", isolateCPUs=False, vswitchCores=1):
    packetSizesBytes = ["64bytes", "512bytes", "1500bytes", "2048bytes"]
    packetSizes = [64, 512, 1500, 2048]

    txDirectionHosts = "dosseplane" # For the filenames and id traffic direction
    rxDirectionHosts = "planedosse" # For the filenames and id traffic direction
    txInterface = "dag0:6" # The interface that transmits the packets
    rxInterface = "dag0:2" # The interface that receives the forwarded packets
    trial = 0 # Number of trials/repetitions
    throughput = 10000 # Throughput of the packets sent to the NIC
    perTenantLatPlotNames = [] # Initial empty list of perTenantLatency figure file names
    print("[*] Going to test the foll. packet size: " + str(packetSizesBytes))
    print("[*] Going to test the foll.:" + topology + ", " + vswitchMode)
    print("[*] Create log directory")
    experiment = "latency"

    # Create a unique directory on disk to save data, e.g., files.
    pcapDataPath = preparePcapDataPath(monitor, logTimeStamp, experiment, topology, vswitchMode, isolateCPUs)

    # Create a unique directory on disk to save analyzed data, e.g., parsed data
    pcapAnalysisPath = preparePcapAnalysisPath(monitor, logTimeStamp, experiment, isolateCPUs)

    # Make sure the monitor is not already capturing data
    cleanUpPacketOperators(cnx=monitor)

    # Collect measurement data for the different packet sizes
    for packetSize, packetLen in zip(packetSizesBytes, packetSizes):
        print("[*] Measuring, packetsize: " + str(packetSize) + ", topology: " + topology + ", vswitchMode: " + vswitchMode + ", cpuIsolation: " + str(isolateCPUs))

        # Sleep to avoid multicast packets sent from the VFs of the tenant VMs
        if topology == "phy2vm2vm2phy" or "vm2vm":
            time.sleep(20)

        ########################################################################
        # dagsnap is used for latency measurements as we want to collect
        # the transmitted and received packets to compute the per packet
        # latency.
        # If using tcpdump we capture the packets and then compute the
        # throughput on the pcaps.
        ########################################################################
        if packetCaptureTool == "dagsnap":
            txCaptureFileName = topology + "-latency-" + vswitchMode + "-" + txDirectionHosts + "-" + packetSize + "-" + str(trial) + ".erf"
            rxCaptureFileName = topology + "-latency-" + vswitchMode + "-" + rxDirectionHosts + "-" + packetSize + "-" + str(trial) + ".erf"
        elif packetCaptureTool == "tcpdump":
            txCaptureFileName = topology + "-latency-" + vswitchMode + "-" + txDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
            rxCaptureFileName = topology + "-latency-" + vswitchMode + "-" + rxDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
        trafficFile = "" # the file name that contains packets to be replayed
        trafficPath = "/root/replay/single-multi-tenant/" # the path to it

        ########################################################################
        # The packet file names are created based on the vswitch mode traffic
        # scenario/topology and packet size, hence we have to set trafficFile
        # accordingly.
        ########################################################################
        if topology == "phy2vm2vm2phy" or topology == "phy2phy":
            if vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "Baseline_NoDPDK":
                trafficFile = "SingleOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "Baseline_DPDK":
                trafficFile = "SingleOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_DPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_NoDPDK_FourOvs":
                trafficFile = "FourOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_DPDK_FourOvs":
                trafficFile = "FourOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
            if trafficFile == "":
                print("[!] Could not set the traffic file!")
                break
        elif topology == "vm2vm":
            if vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "Baseline_NoDPDK":
                trafficFile = "SingleOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "Baseline_DPDK":
                trafficFile = "SingleOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
            elif vswitchMode == "SRIOV_DPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
            if trafficFile == "":
                print("[!] Could not set the traffic file!")
                break

        ########################################################################
        # Measurements are now ready to be made.
        # We first start capturing packets on the tx and rx interfaces
        # respectively, wait 10s and then start the packet generator. When using
        # higher throughput rates, e.g., 14 Mpps, packets need to be captured
        # after the packet generator (dagflood) has started. This is currently
        # not supported.
        ########################################################################
        if packetCaptureTool == "dagsnap":
            print("[+] Starting measurement. The time is: " + str(datetime.now()))
            startPacketCapture(cnx=monitor,interface=txInterface,fileName=txCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision=tsPrecision, tool=packetCaptureTool)
            startPacketCapture(cnx=monitor,interface=rxInterface,fileName=rxCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision=tsPrecision, tool=packetCaptureTool)
            # Wait 10s before starting packet gen
            time.sleep(10)
            print("    Starting packet gen.")
            startEndacePktGen(cnx=monitor, throughput=str(throughput), loop=110000, trafficFile=trafficFile, limitTime=True, time=throughputTestTime,
                              packet_replay_path=trafficPath, background=False)
        print("[*] Finished transmitting packets.")
        print("    Stopping the packet capture")
        stopPacketCapture(cnx=monitor)

        ########################################################################
        # Latency Computation
        # Current limitation: no nanosecond latency computation although the
        # packets have nanosecond time stamps.
        # When using dagsnap, we need to first convert the file to the well
        # [1] Convert the file to the well known pcap format
        # [2] Generate the per-packet timestamps using tcpdump
        # [3] Compute the latency for each packet on a per-tenant basis.
        # Note the filters need to have the appropriate IP addresses and when
        # using the vm2vm topology, there are only 2 tenants.
        ########################################################################
        print("Converting the erf to pcap")
        pcapFiles = covertErfToPcap(cnx=monitor, pcapDataPath=pcapDataPath,
                        pcapFiles=[txCaptureFileName, rxCaptureFileName])
        print("Now timestamp the packets")
        filters = {"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.3",
                   "tenant3": "dst 10.0.0.4", "tenant4": "dst 10.0.0.5"}
        if topology == "vm2vm":
            filters = {"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.4"}
        timeStampPackets(monitor, pcapDataPath, pcapFiles, pcapAnalysisPath, filters,
                         packetSizeFilter="greater " + str(packetLen - 4) +\
                                               " and " + "less " + str(packetLen))
        latencyDict = computeLatencyMulti(monitor, pcapAnalysisPath, pcapFiles, topology,
                                          vswitchMode, packetSize, filters, throughput,
                                          throughputTestTime, startOffset=startOffset, endOffset=endOffset)

        # scp the data to a data storage system
        print("scp the files to plot")
        scp(monitor, store, pcapAnalysisPath, ["*-latency-*.res"], pcapAnalysisPath)

        # Visualize the latency
        print("plotting the latency for multiple tenants")
        plotLatencySplit(pcapAnalysisPath, topology)

        ########################################################################
        # To save disk space the pcaps can be compressed using
        # pigz which may need to be installed if not already available
        ########################################################################
        if packetCaptureTool == "dagsnap":
            print("compressing pcaps and deleting erf files")
            if compressPcapFiles(monitor, pcapDataPath, [txCaptureFileName+".pcap", rxCaptureFileName+".pcap"]) is True:
                print("Pcap files are now compressed: ")
                print("Removing the erf and pcap files")
                removePcapFiles(monitor, pcapDataPath, [txCaptureFileName, rxCaptureFileName])
                removePcapFiles(monitor, pcapDataPath, [txCaptureFileName+".pcap", rxCaptureFileName+".pcap"])

        # Finally clean up capturing on the monitor
        print("Cleanup packetOperators: dagflood, " + packetCaptureTool)
        cleanUpPacketOperators(monitor)

    # Email the plot if set to True
    if emailPlots is True:
        print("emailing the plots")
        EmailNotify("Latency setup is " + str(topology) + ", " +
                        str(vswitchMode) + ", " + str(isolateCPUs) +
                        ". Plot for " + topology + " at " + str(throughput) + " (pps) for four tenant latency attached: " + str(datetime.now()),
                        ": Latency measurement done.",
                        datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                        attachmentPath=pcapAnalysisPath + 'plot_box_latency_' + topology + '-4Tenants-Split.png')

def main():
    # Three different traffic scenarios
    topologies = ["phy2phy", "phy2vm2vm2phy", "vm2vm"]
    # All the different vswitch modes
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
    dut = cnx_plane
    # If the system should isolate the vswitch vm cores or not
    isCPUIsolated = [False, True]

    print("[*] topologies: " + str(topologies))
    print("[*] vswitchModes: " + str(vswitchModes))
    print("[*] isCPUIsolated: " + str(isCPUIsolated))
    print("[*] dut: " + str(dut))

    exp_start_time = datetime.now()
    print("[+] Script started at: " + str(logTimeStamp))

    ############################################################################
    # Latency measurement methodology
    # [1] Iterate through each of the following.
    # 	* cpu isolation mode
    # 	* topology
    # 	* vswitch mode
    # [2] Prepare the server accordingly
    # [3] If that was successful, start the measurements
    # [4] If emails are enabled, send an email after a latency measurement
    #     has completed.
    # [5] Repeat till all configuration permutations are done.
    ############################################################################
    for cpuIsolation in isCPUIsolated:
        for topology in topologies:
            for vswitchMode in vswitchModes:
                vswitchCore = getNbrCores(vswitchMode, cpuIsolation)
                print("vswitchCore: " + str(vswitchCore))
                ################################################################
                # Next prepare the server, e.g., allocate cores, set-up the
                # vswitch vms, run the l2fwd apps in the tenant vms
                ################################################################
                result = prepTestbed(dut, topology, vswitchMode, isolateCPUs=cpuIsolation, vswitchCores=vswitchCore)
                if result is True:
                    start = datetime.now()
                    EmailNotify("Latency setup is" + str(dut) + ", " + str(topology) + ", " +
                                    str(vswitchMode) + ", " + str(cpuIsolation),
                                    ": Latency measurements going to start now.",
                                    start.strftime("%Y-%m-%d_%H-%M-%S"))
                    latency(topology=topology, vswitchMode=vswitchMode,
                               isolateCPUs=cpuIsolation, vswitchCores=vswitchCore)
                    EmailNotify("Latency setup is" + str(dut) + ", " + str(topology) + ", " +
                                    str(vswitchMode) + ", " + str(cpuIsolation) +
                                    "Time to test latency is: " + str(datetime.now() - start),
                                    ": Latency measurement done.",
                                    datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                    print("Time to test latency is: " + str(datetime.now() - start))
        print("[·] Total experiment run time is: " + str(datetime.now() - exp_start_time))

if __name__ == "__main__":
    main()

