from visualizer import *

pcapAnalysisPathLatencyShared = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-submission/latency/sharedCPU/10kppsNic/"
pcapAnalysisPathLatencyIsolated = "/home/hashkash/Documents/TUB/my_work/netVirtSec/secureDataPlane/evaluation/analysis/atc-submission/latency/isolatedCPU/10kppsNic/"
pcapAnalysisPaths = [pcapAnalysisPathLatencyShared, pcapAnalysisPathLatencyIsolated]
experiments = ["throughput", "latency"]
topologies = ["phy2phy", "phy2vm2vm2phy", "vm2vm"]
vswitchModes = ["SRIOV_NoDPDK_OneOvs",
                "SRIOV_NoDPDK_TwoOvs",
                "SRIOV_NoDPDK_FourOvs",
                "Baseline_NoDPDK",
                "SRIOV_DPDK_OneOvs",
                "SRIOV_DPDK_TwoOvs",
                "SRIOV_DPDK_FourOvs",
                "Baseline_DPDK"]

print "topologies: " + str(topologies)
print "vswitchModes: " + str(vswitchModes)

for pcapAnalysisPath in pcapAnalysisPaths:
    print "pcapAnalysisPath: " + pcapAnalysisPath
    for topology in topologies:
        print "topology: " + topology
        print "plotLatencySplit()"
        plotLatencySplit(pcapAnalysisPath, topology)
