#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from packetOperator import *
from expLib import *
from prepTestbed import *
from visualization.visualizer import *

from datetime import datetime
import pprint

logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
emailPlots = True
packetCaptureTool = "dagsnap"
throughputTestTime = 60
monitor = cnx_dosse
tenants = [cnx_Ptenant1, cnx_Ptenant2, cnx_Ptenant3, cnx_Ptenant4]

def latency(topology="phy2phy", vswitchMode="Baseline_NoDPDK", isolateCPUs=False, vswitchCores=1):
    packetSizesBytes = ["64bytes", "512bytes", "1500bytes", "2048bytes"]
    packetSizes = [64, 512, 1500, 2048]
    txDirectionHosts = "dosseplane"
    rxDirectionHosts = "planedosse"
    txInterface = "dag0:2"
    rxInterface = "dag0:6"
    trial = 0
    throughput = 10000
    print("[+] Going to test the foll. packet size: " + str(packetSizesBytes))
    print("[+] Going to test the foll.:" + topology + ", " + vswitchMode)
    
    # create log directory 
    experiment = "latency"
    pcapDataPath = preparePcapDataPath(monitor, logTimeStamp, experiment, topology, vswitchMode, isolateCPUs)
    pcapAnalysisPath = preparePcapAnalysisPath(monitor, logTimeStamp, experiment, isolateCPUs)
    cleanUpPacketOperators(cnx=monitor)
    for packetSize, packetLen in zip(packetSizesBytes, packetSizes):
        print("[*] Measuring, packetsize: " + str(packetSize) + ", topology: " + topology + ", vswitchMode: " + vswitchMode + ", cpuIsolation: " + str(isolateCPUs))
        if topology == "phy2vm2vm2phy" or "vm2vm":
            # sleep 20s before starting packet capture to avoid capturing multicast packets
            time.sleep(20)
        if packetCaptureTool == "dagsnap":
            txCaptureFileName = topology + "-latency-" + vswitchMode + "-" + txDirectionHosts + "-" + packetSize + "-" + str(trial) + ".erf"
            rxCaptureFileName = topology + "-latency-" + vswitchMode + "-" + rxDirectionHosts + "-" + packetSize + "-" + str(trial) + ".erf"
        else:
            txCaptureFileName = topology + "-latency-" + vswitchMode + "-" + txDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
            rxCaptureFileName = topology + "-latency-" + vswitchMode + "-" + rxDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
        trafficFile = ""
        trafficPath = "/root/replay/single-multi-tenant/"

        if topology == "phy2vm2vm2phy" or topology == "phy2phy":
            if vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "Baseline_NoDPDK":
                trafficFile = "SingleOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "Baseline_DPDK":
                trafficFile = "SingleOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_DPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_NoDPDK_FourOvs":
                trafficFile = "FourOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_DPDK_FourOvs":
                trafficFile = "FourOvsVm-4tenants-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            if trafficFile == "":
                print("[!] Could not set the traffic file!")
                break
        elif topology == "vm2vm":
            if vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "Baseline_NoDPDK":
                trafficFile = "SingleOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_DPDK_OneOvs" or vswitchMode == "Baseline_DPDK":
                trafficFile = "SingleOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_NoDPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            elif vswitchMode == "SRIOV_DPDK_TwoOvs":
                trafficFile = "TwoOvsVm-4tenants-VMVM-latency-"+packetSize+"-port0.erf"
                throughput = 10000
            if trafficFile == "":
                print("Could not set the traffic file!")
                break

        throughputTestTime = 30
        print("throughput: " + str(throughput) + ", throughputTestTime: " + str(throughputTestTime))

        if packetCaptureTool == "dagsnap":
            print("[*] Starting measurement! The time is: " + str(datetime.now()))
            startPacketCapture(cnx=monitor,interface=txInterface,fileName=txCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision="micro", tool=packetCaptureTool)
            startPacketCapture(cnx=monitor,interface=rxInterface,fileName=rxCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision="micro", tool=packetCaptureTool)
            print("Wait 10s before starting packet gen.")
            time.sleep(10)
            print("Starting packet gen.")
            startEndacePktGen(cnx=monitor, throughput=str(throughput), loop=110000, trafficFile=trafficFile, limitTime=True, time=throughputTestTime,
                              packet_replay_path=trafficPath, background=False)
        print("[*] Finished transmitting packets.")
        print("Stopping the packet capture")
        stopPacketCapture(cnx=monitor)

        print("converting the erf to pcap")
        pcapFiles = covertErfToPcap(cnx=monitor, pcapDataPath=pcapDataPath,
                        pcapFiles=[txCaptureFileName, rxCaptureFileName])
        print("[*] timestamping the packets")
        filters = {"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.3",
                   "tenant3": "dst 10.0.0.4", "tenant4": "dst 10.0.0.5"}
        if topology == "vm2vm":
            filters = {"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.4"}
        timeStampPackets(monitor, pcapDataPath, pcapFiles, pcapAnalysisPath, filters,
                         packetSizeFilter="greater " + str(packetLen - 4) +\
                                               " and " + "less " + str(packetLen))
        latencyDict = computeLatencyMulti(monitor, pcapAnalysisPath, pcapFiles, topology,
                                          vswitchMode, packetSize, filters, throughput,
                                          throughputTestTime, startOffset=10, endOffset=10)

        # scp the files to plot)
        scp(monitor, cnx_spree, pcapAnalysisPath, ["*-latency-*.res"], pcapAnalysisPath)
 
        print("plotting the latency for multiple tenants")
        plotLatencySplit(pcapAnalysisPath, topology)
        if isolateCPUs is False:
            resourceType = "shared"
        else:
            resourceType = "isolated"
        perTenantLatPlotName = plotLatencyPerTenant(pcapAnalysisPath, resourceType=resourceType, topology=topology,
                                                    throughput=throughput, time=throughputTestTime, startOffset=10,
                                                    endOffset=10, tenantCount=len(filters.keys()))

        if packetCaptureTool == "dagsnap":
            print("compressing pcap and delete the erf")
            if compressPcapFiles(monitor, pcapDataPath, [txCaptureFileName+".pcap", rxCaptureFileName+".pcap"]) is True:
                print("Pcap files are now compressed: ")
                print("Removing erf and pcap files")
                removePcapFiles(monitor, pcapDataPath, [txCaptureFileName, rxCaptureFileName])
                removePcapFiles(monitor, pcapDataPath, [txCaptureFileName+".pcap", rxCaptureFileName+".pcap"])

        print("Cleanup packetOperators: dagflood, " + packetCaptureTool)
        cleanUpPacketOperators(monitor)

    if emailPlots is True:
        print("Now email the plots")
        EmailNotify("Latency setup is " + str(topology) + ", " +
                        str(vswitchMode) + ", " + str(isolateCPUs) +
                        ". Plot for " + topology + " at " + str(throughput) + " (pps) for four tenant latency attached: " + str(datetime.now()),
                        ": Latency measurement done.",
                        datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                        attachmentPath=pcapAnalysisPath + 'plot_box_latency_' + topology + '-4Tenants-Split.png')
        EmailNotify("Latency setup is " + str(topology) + ", " +
                        str(vswitchMode) + ", " + str(isolateCPUs) +
                        ". Plot for per tenant/vswitch " + topology + " at " + str(throughput) + " (pps) for four tenant latency attached: " + str(datetime.now()),
                        ": Latency measurement done.",
                        datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                        attachmentPath=pcapAnalysisPath + perTenantLatPlotName)

def main():
    topologies = ["phy2phy", "phy2vm2vm2phy"]
    vswitchModes = ["SRIOV_NoDPDK_Dynamic_Container"]
    container_config = [1, 2, 16]
    isCPUIsolated = [False, True]

    dut = cnx_plane

    print("topologies: " + str(topologies))
    print("vswitchModes: " + str(vswitchModes))
    print("isCPUIsolated: " + str(isCPUIsolated))
    print("dut: " + str(dut))

    exp_start_time = datetime.now()
    print("[+] Script started at: " + str(logTimeStamp))

    for cpuIsolation in isCPUIsolated:
        for topology in topologies:
            for vswitchMode in vswitchModes:
                vswitchCore = getNbrCores(vswitchMode, cpuIsolation)
                print("vswitchCore: " + str(vswitchCore))
                result = prepTestbed(dut, topology, vswitchMode, isolateCPUs=cpuIsolation, vswitchCores=vswitchCore, containerConfig=container_config)

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
