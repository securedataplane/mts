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
from packetOperator import *

txDirectionHosts = "elbeplane"
rxDirectionHosts = "planeelbe"
txInterface = "dag0:2"
rxInterface = "dag0:6"
trial = 0

packetSizesBytes = ["64bytes", "512bytes", "1500bytes", "2048bytes"]
packetSizes = [64, 512, 1500, 2048]
packetSizesBytes = ["64bytes", "512bytes"]
packetSizes = [64, 512]
packetSizesBytes = ["1500bytes", "2048bytes"]
packetSizes = [1500, 2048]
lat_packet_start_index = 100
lat_packet_end_index = 10100

topologies = ["phy2phy", "phy2vm2vm2phy"]
topologies = ["phy2phy"]
topologies = ["phy2vm2vm2phy"]

vswitchModes = ["Baseline_NoDPDK", "SRIOV_NoDPDK", "SRIOV_DPDK",
                "Baseline_MultiTenant_NoDPDK", 
                "SRIOV_MultiTenant_NoDPDK", "SRIOV_MultiTenant_DPDK",
                "SRIOV_MultiOvs_NoDPDK", "SRIOV_MultiOvs_DPDK"]
vswitchModes = ["Baseline_NoDPDK", "SRIOV_NoDPDK", "SRIOV_DPDK",
                "Baseline_MultiTenant_NoDPDK", 
                "SRIOV_MultiTenant_NoDPDK", "SRIOV_MultiTenant_DPDK",
                "SRIOV_MultiOvs_NoDPDK"]
vswitchModes = ["SRIOV_MultiOvs_NoDPDK", "SRIOV_MultiOvs_DPDK"]
vswitchModes = ["Baseline_NoDPDK", "SRIOV_NoDPDK"]
vswitchModes = ["Baseline_MultiTenant_NoDPDK", "SRIOV_MultiTenant_NoDPDK"]
vswitchModes = ["SRIOV_DPDK"]

isCPUIsolated = [False, True]
isCPUIsolated = [False]
isCPUIsolated = [True]
isCPUIsolated = [False]

logTimeStamp = "2018-09-02_03-06-46"
logTimeStamp = "2018-09-02_21-23-44"
logTimeStamp = "2018-09-02_03-06-46"
logTimeStamp = "2018-09-03_01-19-00"
logTimeStamp = "2018-09-02_03-06-46"
logTimeStamp = "2018-09-03_11-54-07"

print "topologies: " + str(topologies)
print "vswitchModes: " + str(vswitchModes)

for isolateCPUs in isCPUIsolated:
    for topology in topologies:
        for vswitchMode in vswitchModes:
            # result = True
            if isolateCPUs is True:
                if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "SRIOV_NoDPDK" or \
                        vswitchMode == "SRIOV_DPDK" or vswitchMode == "Baseline_MultiTenant_NoDPDK" or \
                        vswitchMode == "SRIOV_MultiTenant_NoDPDK" or vswitchMode == "SRIOV_MultiTenant_DPDK":
                    continue
            experiment = "latency"
            pcapDataPath = ""
            pcapAnalysisPath = ""
            if isolateCPUs is False:
                pcapDataPath = "/root/data/" + logTimeStamp + "/" + experiment + "/" + "sharedCPU" + "/" + topology+ "/" + vswitchMode + "/"
                pcapAnalysisPath = "/root/analysis/"+logTimeStamp+"/"+experiment+"/"+"sharedCPU"+"/"
            else:
                pcapDataPath = "/root/data/" + logTimeStamp + "/" + experiment + "/" + "isolatedCPU" + "/" + topology + "/" + vswitchMode + "/"
                pcapAnalysisPath = "/root/analysis/"+logTimeStamp+"/"+experiment+"/"+"isolatedCPU"+"/"
            for packetSize, packetLen in zip(packetSizesBytes, packetSizes):
                ##### MEASUREMENT STUFF ####
                txCaptureFileName = topology + "-latency-" + vswitchMode + "-" + txDirectionHosts + "-" + packetSize + "-" + str(trial) + ".pcap"
                rxCaptureFileName = topology + "-latency-" + vswitchMode + "-" + rxDirectionHosts + "-" + packetSize + "-" + str(trial) + ".pcap"
                ##########################

                #### LATENCY STUFF ####
                print "Now timestamp the packets"
                latencyDict = {}
                filters = {"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.3"}
                if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "Baseline_DPDK" or \
                    vswitchMode == "SRIOV_NoDPDK" or vswitchMode == "SRIOV_DPDK":
                    timeStampPackets(cnx_elbe, pcapDataPath, [txCaptureFileName, rxCaptureFileName], pcapAnalysisPath,
                                     packetSizeFilter="greater " + str(packetLen - 4) + " and " + "less " + str(packetLen))
                    latencyDict=computeLatency(cnx_elbe, pcapAnalysisPath, [txCaptureFileName, rxCaptureFileName], topology, vswitchMode, packetSize)

                else:
                    timeStampPacketsMulti(cnx_elbe, pcapDataPath, [txCaptureFileName, rxCaptureFileName], pcapAnalysisPath, filters,
                                          packetSizeFilter="greater " + str(packetLen - 4) + " and " + "less " + str(packetLen))
                    latencyDict=computeLatencyMulti(cnx_elbe, pcapAnalysisPath, [txCaptureFileName, rxCaptureFileName], topology, vswitchMode, packetSize, filters)
                # #########################
                #
                #
                # #### SCP STUFF ####
                print "scp the files to plot"
                scp(cnx_elbe, cnx_spree, pcapAnalysisPath, ["*-latency-*.res"], pcapAnalysisPath)
                # #########################

