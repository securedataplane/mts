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
packetCaptureTool = "dagbits"
throughputTestTime = 110
monitor = cnx_dosse
tenants = [cnx_Ptenant1, cnx_Ptenant2, cnx_Ptenant3, cnx_Ptenant4]

def throughput(topology="phy2phy", containerConfig=[1,1], isolateCPUs=False, vswitchCores=1):
    vswitchMode = "SRIOV_NoDPDK_Dynamic_Container"
    throughputRates = []
    ratesLow = range(14000000, 15000000, 1000000)
    if vswitchMode == "Baseline_NoDPDK":
        if topology == "phy2vm2vm2phy" or topology == "vm2vm":
            ratesLow = range(500000, 600000, 100000)
    ratesMid = None
    ratesHigh = None
    ratesAll = [ratesLow, ratesMid, ratesHigh]
    for rates in ratesAll:
        if rates is not None:
            throughputRates.extend(rates)
    print("Using following throughputRates")
    print(throughputRates)
    # Efficient throughputRatesPps generation
    throughputRatesPps = []
    for t in throughputRates:
        throughputRatesPps.append(str(str(float(t) / 1000) + "0k"))
    print("Using following throughputRatesPps")
    print(throughputRatesPps)
    txDirectionHosts = "dosseplane"
    rxDirectionHosts = "planedosse"
    txInterface = "dag0:6"
    rxInterface = "dag0:2"
    trial = 0
    print("Going to test the foll. throughput rates: " + str(throughputRates))
    print("Going to test the foll.:" + topology + ", " + containerConfig)
    
    # create log directory")
    experiment = "throughput"
    pcapDataPath = preparePcapDataPath(monitor, logTimeStamp, experiment, topology, vswitchMode, isolateCPUs)
    pcapAnalysisPath = preparePcapAnalysisPath(monitor, logTimeStamp, experiment, isolateCPUs)
    cleanUpPacketOperators(cnx=monitor)
    for throughput in throughputRates:
        print("Measuring, throughput: " + str(throughput) + ", topology: " + topology + ", vswitchMode: " + vswitchMode + ", cpuIsolation: " + str(isolateCPUs) + ", vswitchCores: " + str(vswitchCores))
        print("Sleep 20s before starting packet capture to avoid capturing multicast packets.")
        time.sleep(20)
        if packetCaptureTool == "dagbits":
            txCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + txDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".txt"
            rxCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + rxDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".txt"
        else:
            txCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + txDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
            rxCaptureFileName = topology + "-throughput-" + vswitchMode + "-" + rxDirectionHosts + "-" + str(throughput) + "-" + str(trial) + ".pcap"
        trafficFile = ""
        trafficPath = "/root/replay/single-multi-tenant/"
        ###
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

        if packetCaptureTool == "dagbits":
            print("Starting measurement! The time is: " + str(datetime.now()))
            print("Starting packet gen.")
            startEndacePktGen(cnx=monitor, throughput=str(throughput), loop=210, trafficFile=trafficFile, limitTime=True, time=throughputTestTime,
                              packet_replay_path=trafficPath, background=True)
            print("Start packet capture in 10s")
            time.sleep(10)
            # startPacketCapture(cnx=monitor,interface=txInterface,fileName=txCaptureFileName,
            #                    pcapDataPath=pcapDataPath, timestamp_precision="micro", tool="dagbits")
            startPacketCapture(cnx=monitor,interface=rxInterface,fileName=rxCaptureFileName,
                               pcapDataPath=pcapDataPath, timestamp_precision="micro", tool="dagbits")
            print("Now sleep for " + str(throughputTestTime) + ", so that packet gen and capture have completed")
            time.sleep(throughputTestTime)
        print("[*] Finished transmitting packets.")
        print("[*] Stopping the packet capture")
        stopPacketCapture(cnx=monitor)

        print("[*] Computing throughput")
        # # Can't run computeThroughput() on nanosecond pcap files
        computeThroughput(monitor, pcapDataPath,
                          [rxCaptureFileName],
                          pcapAnalysisPath, topology, vswitchMode,
                          throughput, packetCaptureTool=packetCaptureTool)

        print("scp the files to plot")
        if packetCaptureTool == "dagbits":
            scp(monitor, cnx_spree, pcapAnalysisPath, ["*-throughput-*-0.txt"], pcapAnalysisPath)
        else:
            scp(monitor, cnx_spree, pcapAnalysisPath, ["*-throughput-*-0.pcap"], pcapAnalysisPath)

        print("Plot the throughput")
        if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "Baseline_DPDK" or \
            vswitchMode == "SRIOV_NoDPDK" or vswitchMode == "SRIOV_DPDK":
            print("plot the throughput for single tenant")
            plotThroughput(pcapAnalysisPath, topology)
        elif vswitchMode == "Baseline_MultiTenant_NoDPDK" or vswitchMode == "Baseline_MultiTenant_DPDK" or \
            vswitchMode == "SRIOV_MultiTenant_NoDPDK" or vswitchMode == "SRIOV_MultiTenant_DPDK" or \
                vswitchMode == "SRIOV_MultiOvs_NoDPDK" or vswitchMode == "SRIOV_MultiOvs_DPDK":
            print("plot the throughput for multiple tenants")
            plotThroughputMulti(pcapAnalysisPath, topology)
        tabulateTput(pcapAnalysisPath, topology, vswitchMode, isolateCPUs, [rxCaptureFileName], throughput)

        if packetCaptureTool == "tcpdump":
            print("Now compress pcaps")
            print("Pcap files are now compressed: ")
            if compressPcapFiles(monitor, pcapDataPath, [txCaptureFileName, rxCaptureFileName]) is True:
                print("Removing the pcap files")
                removePcapFiles(monitor, pcapDataPath, [txCaptureFileName, rxCaptureFileName])

        print("Cleanup packetOperators: dagflood, " + packetCaptureTool)
        time.sleep(5)
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
    topologies = ["phy2phy", "phy2vm2vm2phy"]
    vswitchMode = "SRIOV_NoDPDK_Dynamic_Container"
    container_configs = [[1, 1],
                         [1, 2],
                         [1, 4],
                         [1, 8],
                         [2, 2],
                         [2, 8],
                         [2, 16],
                         [2, 32]
                         ]
    dut = cnx_plane
    isCPUIsolated = [False, True]

    print("topologies: " + str(topologies))
    print("Container Configs: " + str(container_configs))
    print("isCPUIsolated: " + str(isCPUIsolated))
    print("dut: " + str(dut))

    exp_start_time = datetime.now()
    print("Script started at: " + str(logTimeStamp))

    for cpuIsolation in isCPUIsolated:
        for topology in topologies:
            for conf in container_configs:
                vswitchCore = getNbrCores(vswitchMode, cpuIsolation)
                print("vswitchCore: " + str(vswitchCore))
                # result = True
                result = prepTestbed(dut, topology, vswitchMode, isolateCPUs=cpuIsolation, vswitchCores=vswitchCore, containerConfig=conf)
                if result is True:
                    start = datetime.now()
                    EmailNotify("Throughput setup for Dynamic_Container is" + str(dut) + ", " + str(topology) + ", " +
                                    str(conf) + ", " + str(cpuIsolation),
                                    ": Throughput measurements going to start now.",
                                    start.strftime("%Y-%m-%d_%H-%M-%S"))
                    throughput(topology=topology, vswitchMode=vswitchMode,
                               isolateCPUs=cpuIsolation, vswitchCores=vswitchCore)
                    EmailNotify("Throughput setup is" + str(dut) + ", " + str(topology) + ", " +
                                    str(vswitchMode) + ", " + str(cpuIsolation) +
                                    "Time to test throughput is: " + str(datetime.now() - start),
                                    ": Throughput measurement done.",
                                    datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                    print("Time to test throughput is: " + str(datetime.now() - start))
        print("Total experiment run time is: " + str(datetime.now() - exp_start_time))


def debug():
    start = datetime.now()
    print("Time to init testbed is: " + str(datetime.now() - start))
    dut = cnx_plane
    print("First start l2fwd due to multicast sent when link comes up")
    startL2fwdDpdk(cnx_Ptenant1, vswitchMode="SRIOV_2Ovs_4Tenants", nicType="mlx", tenantNumber="1")
    print("l2fwd on tenant1 started.")
    startL2fwdDpdk(cnx_Ptenant2, vswitchMode="SRIOV_2Ovs_4Tenants", nicType="mlx", tenantNumber="2")
    print("l2fwd on tenant2 started.")
    startL2fwdDpdk(cnx_Ptenant3, vswitchMode="SRIOV_2Ovs_4Tenants", nicType="mlx", tenantNumber="3")
    print("l2fwd on tenant3 started.")
    startL2fwdDpdk(cnx_Ptenant4, vswitchMode="SRIOV_2Ovs_4Tenants", nicType="mlx", tenantNumber="4")
    # scs.phy2vm2vm2phy_SRIOV_1Ovs_4Tenants(dut, False)
    # startPacketCapture(cnx=cnx_elbe,interface=txInterface,fileName=txCaptureFileName)
    # startPacketCapture(cnx=cnx_elbe,interface=rxInterface,fileName=rxCaptureFileName)
    # print "Start! Time is: " + str(datetime.now())
    # print "Now start replay on elbe using dagflood"
    # startEndacePktGen(cnx=cnx_elbe, throughput="10", loop=1, trafficFile=trafficFile, limitTime=True, time=20)
    print("debug()")

def startL2Frwd(nbrOvs=1, nicType="mlx"):
    for t, tenant in zip(range(1, 5), tenants):
        startL2fwdDpdk(tenant, vswitchMode="SRIOV_"+str(nbrOvs)+"Ovs_4Tenants", nicType=nicType, tenantNumber=str(t))

if __name__ == "__main__":
    # startL2Frwd(1, "e1000")
    main()
    # debug()
