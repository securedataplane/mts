#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A HELPER FOR ALL PACKET RELATED OPERATIONS:
* GENERATION
* REPLAY
* LATENCY
* THROUGHPUT
"""
from expLib import *
import sys
import os
import re
import glob
import numpy as np
import json

# tcpdump_path="/usr/local/tcpdump-dag/sbin/" # tcpdump on elbe
tcpdump_path="/usr/local/sbin/"
packet_capture_path="/root/data/"
packet_replay_path="/root/replay/"

'''
Reset the Endace card using the bash script on the server
Pass the connection as a parameter
'''
def resetEndace(cnx):
    print "Reset endace card before transmit so that tx buffers are empty"
    ssh = SSHConnect(cnx=cnx)
    resetDagCommand="cd /root/endace; sh resetDag.sh"
    RunCommand(ssh, resetDagCommand)
    print "Sleep 3 second so that the link comes up"
    time.sleep(3)
    ssh.close()

'''
Start Endace's packet generator dagflood
@cnx the server to be used for daglood
@throughput the rate at which to transmit
@loop the number of times to loop through the packet file
@trafficFile the file containing the packets(erf file)
@limitTime True/False to stop transmission after a specified time
@time the time after which to stop transmission, needs to have limitTime=True
@packet_replay_path the path to the traffic file
@background True/False to run dagflood in the background or not (different for throughput and latency)
'''
def startEndacePktGen(cnx, throughput, loop, trafficFile, limitTime=False, time=1050, packet_replay_path=packet_replay_path, background=False):
    print "Start endace's dagflood on " + cnx[0]
    ssh = SSHConnect(cnx=cnx)
    if background is False:
        dagfloodCommand = "dagflood -f " + packet_replay_path +\
                          trafficFile + " -R -c " + str(loop) +\
                          " -p " + throughput
        if limitTime is True:
            dagfloodCommand = dagfloodCommand + " -t " + str(time)
    elif background is True:
        dagfloodCommand = "screen -dmSL dagfloodSession dagflood -f " + packet_replay_path +\
                          trafficFile + " -R -c " + str(loop) +\
                          " -p " + throughput
        if limitTime is True:
            dagfloodCommand = dagfloodCommand + " -t " + str(time)
    RunCommand(ssh, dagfloodCommand)
    ssh.close()

'''
Start capturing packets using different tools: tcpdump,dagbits, dagsnap, in a screen session
@cnx the server to run the packet capture
@interface the interface to capture packets on
@filename the name of the file to save the captured packets to
@pcapDataPath the path to the file of captured packets
@timestamp_precision micro/nano precision level for capturing packets; this is only for tcpdump
@tool tcpdump/dagbits/dagsnap are currently the supported capture tools
'''
def startPacketCapture(cnx, interface, fileName, pcapDataPath=packet_capture_path, timestamp_precision="micro", tool="tcpdump"):
    print "Going to start the packet capture on " + cnx[0] + " on interface:" + interface
    ssh = SSHConnect(cnx=cnx)
    if tool == "tcpdump":
        print "start capture with tcpdump"
        RunCommand(ssh, "screen -dmSL tcpdumpSession " + tcpdump_path +\
                   "tcpdump -neK -i " + interface + " -w " + \
                   pcapDataPath + fileName +
                   " --time-stamp-precision="+timestamp_precision)
    elif tool == "dagbits":
        print "start capture with dagbits"
        RunCommand(ssh, "screen -dmSL dagbitsSession bash -c " + \
                   "'dagbits -d " + interface + " > " + \
                   pcapDataPath + fileName + "'" )
    elif tool == "dagsnap":
        print "start capture with dagsnap"
        RunCommand(ssh, "screen -dmSL dagsnapSession bash -c " + \
                   "'dagsnap -d "+interface+" -o "+ \
                   pcapDataPath + fileName + "'")
        ssh.close()

'''
Stop capturing packets. Just kill the screen sessions
@cnx the server running the packet capture
'''
def stopPacketCapture(cnx):
    print "Going to stop the packet capture on " + cnx[0]
    ssh = SSHConnect(cnx=cnx)
    RunCommand(ssh, "screen -ls | grep Detached | cut -d . -f1 | awk '{print $1}' | xargs kill")
    ssh.close()

'''
Used to convert erf to pcap using dagconvert.
The pcap files will be saved with the same name as the erf file
@cnx the server that has the dagconvert tool
@pcapDataPath the path to the captured packet files
@pcapFiles a list of erf file to be converted to pcap
'''
def covertErfToPcap(cnx, pcapDataPath=packet_capture_path, pcapFiles=[]):
    print "covertErfToPcap()"
    ssh = SSHConnect(cnx=cnx)
    dagconvertCommand = "dagconvert -T erf:pcap -i "
    files = []
    for pcapFile in pcapFiles:
        RunCommand(ssh, "cd " + pcapDataPath + "; " + dagconvertCommand + pcapFile +\
                    " -o " + pcapFile + ".pcap")
        files.append(pcapFile+".pcap")
    ssh.close()
    return files

'''
Stop packet capturing and reset the Endace card
@cnx the server that runs the packet capture and endace card
(currently they are on the same system)
'''
def cleanUpPacketOperators(cnx):
    print "Kill any existing captures"
    stopPacketCapture(cnx=cnx)
    print "Reset the Endace DAG card so that tx buffers are empty"
    resetEndace(cnx=cnx)

'''
Initialize the server with the endace card
[1] First reboot the system
[2] Run the bringUpDag script on the system
@cnx the server with the endace card
'''
def initializeEndace(cnx):
    print "initializeEndace()"
    print "First reboot Elbe"
    RebootServer(cnx)
    print "Wait for Elbe to come up..."
    time.sleep(30)
    ssh =  SSHConnect(cnx)
    RunCommand(ssh, "cd /root/endace; sh bringUpDag.sh")
    ssh.close()
    print "The Dag card on Elbe has been brought up."

'''
To bring up the links on a list of interfaces on a server
@cnx the server that needs the links to be set
@interfaces list of interfaces to be set up
'''
def upInterfaces(cnx, interfaces):
    print "upInterfaces"
    ssh = SSHConnect(cnx)
    for interface in interfaces:
        RunCommand(ssh, "ip link set " + interface + " up;")
    ssh.close()

'''
Makes directories for data from an experimental run based on the parameters set.
The date provides a unique folder and within each of those unique
directories is a similar directory structure based on the parameters.
@cnx the server on which the pcapDataPath needs to be created
@date the date
@experiment throughput/latency
@topology the different topologies: phy2phy, phy2vm2vm2phy, etc.
@vswitchMode the different vswitch modes: SRIOV_NoDPDK, etc.
@isolateCPUs True/False whether cpu isolation is enabled
'''
def preparePcapDataPath(cnx, date, experiment, topology, vswitchMode, isolateCPUs):
    print "preparePcapDataPath()"
    ssh = SSHConnect(cnx)
    if isolateCPUs == False:
        RunCommand(ssh, "mkdir -p /root/data/"+date+"/"+experiment+"/"+"sharedCPU"+"/"+topology+"/"+vswitchMode+"/")
        ssh.close()
        return "/root/data/"+date+"/"+experiment+"/"+"sharedCPU"+"/"+topology+"/"+vswitchMode+"/"
    elif isolateCPUs == True:
        RunCommand(ssh, "mkdir -p /root/data/"+date+"/"+experiment+"/"+"isolatedCPU"+"/"+topology+"/"+vswitchMode+"/")
        ssh.close()
        return "/root/data/"+date+"/"+experiment+"/"+"isolatedCPU"+"/"+topology+"/"+vswitchMode+"/"

'''
Requires pigz installed.
This compresses the pcapfiles passed and keeps the original files
@cnx the server that will use pigz to comprese the files
@pcapPath the path to the pcap files that need to be compressed
@pcapFiles a list of pcapFiles that need to be compressed.
'''
def compressPcapFiles(cnx, pcapPath, pcapFiles):
    print "Call \"pigz -5 -v \" on host" + str(cnx) + "for the following files:" + str(pcapFiles)
    ssh = SSHConnect(cnx)
    pigzCommand = "pigz --keep -5 -v "
    compressedPcapFiles = []
    for pcapFile in pcapFiles:
        RunCommand(ssh, "cd " + pcapPath + "; " + pigzCommand + pcapFile)
        compressedPcapFiles.append(pcapFile+".gz")
    ssh.close()
    return True

'''
Remove unwanted pcapFiles (Be careful when using this!)
@cnx the server on which to remove the pcap files
@pcapPath the path to the files to be deleted
@pcapFiles list of files to be deleted
'''
def removePcapFiles(cnx, pcapPath, pcapFiles):
    ssh = SSHConnect(cnx)
    removePcapCommand = "rm -f "
    for pcapFile in pcapFiles:
        RunCommand(ssh, "cd " + pcapPath + "; " + removePcapCommand + pcapFile)
    ssh.close()

'''
Similar to preparePcapDataPath(), however, here we create another path (*/analysis/*)
for the analyzed data and we store all of them within a single experiment and
cpu isolation mode.
@cnx server on which the analysis path is to be created
@date the date timestamp
@experiment throughput/latency
@isolateCPUs the cpu isolation mode True/False will result in isolatedCPU/sharedCPU resp. 
'''
def preparePcapAnalysisPath(cnx, date, experiment, isolateCPUs ):
    print "preparePcapAnalysisPath()"
    ssh = SSHConnect(cnx)
    if isolateCPUs == False:
        RunCommand(ssh, "mkdir -p /root/analysis/"+date+"/"+experiment+"/"+"sharedCPU")
        ssh.close()
        return "/root/analysis/"+date+"/"+experiment+"/"+"sharedCPU"+"/"
    elif isolateCPUs == True:
        RunCommand(ssh, "mkdir -p /root/analysis/"+date+"/"+experiment+"/"+"isolatedCPU")
        ssh.close()
        return "/root/analysis/"+date+"/"+experiment+"/"+"isolatedCPU"+"/"

'''
Print timestamps for each packet and save them to a file using tcpdump(4.8.1)
Although the saved file has a .pcap extension, it is a regular text file.
Furthermore, the file saved is tenant specific, i.e., it contains timestamps
only for packets that matched the filter.
Based on the default values, you will have a tx/rx timestamp file for tenant1 with
packets that have 10.0.0.2 as the destination ip address and another tx/rx timestamp
file for tenant2 with packets tht have 10.0.0.3 as the destination ip address.
@cnx the server that has tcpdump installed and the pcap files
@sourcePcapPath path to the pcap files that need to be timestamped
@sourcePcapFiles the list of pcap files [tx, rx] that need to be timestamped
@destPcapPath the path where the timestamped packets are to be saved
@filters a dictionary of filters, the key is the name for the filter that will be appended
to the timestamped file and the value is the tcpdump filter to be applied to the pcap file
for timestamping
@packetSizeFilter a tcpdump filter based on the packet sizes applied to the source pcap file 
'''
def timeStampPackets(cnx, sourcePcapPath, sourcePcapFiles, destPcapPath,
                     filters={"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.3"},
                     packetSizeFilter = ""):
    ssh = SSHConnect(cnx)
    for filter in filters.keys():
        timeStampCommand = ""
        if packetSizeFilter == "":
            timeStampCommand = tcpdump_path + "tcpdump.4.8.1 -n -tt --time-stamp-precision=micro "+filters[filter] +\
                               " -r "
        else:
            timeStampCommand = tcpdump_path + "tcpdump.4.8.1 -n -tt --time-stamp-precision=micro "+filters[filter] +\
                               " and " + packetSizeFilter + " -r "
        RunCommand(ssh, "mkdir -p " + destPcapPath)
        for pcapFile in sourcePcapFiles:
            RunCommand(ssh, "cd " + sourcePcapPath + "; " + timeStampCommand + pcapFile + " > " +\
                        destPcapPath + pcapFile + "-" + filter)
    ssh.close()

'''
Extracts the throughput either using tracereport or dagbits depending on
whether tcpdump or dagbits was used to collect throughput data.
Note traceutils needs to be installed to use tracereport.
@cnx the server to run the throughput computation tool
@sourcePcapPath the path to the source pcap files/dagbits output file
@destPcapPath the path to where the throughput information should be saved
@packetCaptureTool currently tcpdump/dagbits for tcpdump and dagbits
'''
def computeThroughput(cnx, sourcePcapPath, sourcePcapFiles, destPcapPath, packetCaptureTool="tcpdump"):
    ssh = SSHConnect(cnx)
    traceReportCommand = "tracereport -m "
    RunCommand(ssh, "mkdir -p " + destPcapPath)
    if packetCaptureTool == "tcpdump":
        for pcapFile in sourcePcapFiles:
            RunCommand(ssh, "cd " + sourcePcapPath + "; " + traceReportCommand + pcapFile +\
                        "; mv misc.rpt " + destPcapPath + pcapFile)
    elif packetCaptureTool == "dagbits":
        for pcapFile in sourcePcapFiles:
            RunCommand(ssh, "cd " + sourcePcapPath + "; cp " + pcapFile + " " + destPcapPath + pcapFile)
            RunCommand(ssh, "cd " + sourcePcapPath + "; cat " + pcapFile)

'''
Computes the per packet latency from the timestamped packets.
For unmarked packets, a start and end offset in combination with
the throughput are used to ignore packets at the start and end of
packet transmission/forwarding. The per-packet latency is simply
the time difference between the rx (forwarded) packet and tx
(transmitted) packet.

The tenant throughput (tenantTput) is a fraction of the throughput of packets sent to the NIC
The startIndex is the number of packets to skip forward from the packets which is the @startOffset*tenantTput
Similarly the endIndex is the number of packets to skip backwards from the end of the packets which 
is @endOffset*tenantTput.

We create dictionaries based on @filters keys and store the (per-tenant) latencies in there.
Finally we merge the per-tenant latency dictionaries into one big latency dictionary that is
then saved in the @pcapAnalysisPath for the specific experiment.

@cnx the server on which to compute the latency
@pcapAnalysisPath the path in which the computed latencies should be saved
@pcapFiles the list of per-packet timestamped files, e.g., [tx.pcap, rx.pcap]
@topology the different topologies
@vswitchMode the different vswitch modes
@pktSize the different packet sizes
@filters a dict of the filters as shown in the default
@throughput the default value is 10000 pps, an integer value
@time the total time in seconds packets were transmitted/forwarded
@startOffset the time in seconds to skip forward from the start of packets
@endOffset the time in seconds to ignore from the end of packets
'''
def computeLatencyMulti(cnx, pcapAnalysisPath, pcapFiles, topology, vswitchMode, pktSize, filters={"tenant1": "dst 10.0.0.2", "tenant2": "dst 10.0.0.3"},
                        throughput=10000, time=50, startOffset=10, endOffset=10):
    print "computeLatency()"
    ssh = SSHConnect(cnx)
    ###########################################################################
    # Compute the tenant throughput,
    # the start and end offsets/index values
    ###########################################################################
    tenants = len(filters.keys())
    tenantTput = throughput/tenants
    startIndex = tenantTput*startOffset
    endIndex = tenantTput*(time - endOffset - 1) # subtract one to avoid errors
    print "Start and end Index:" + str(startIndex) + ", " + str(endIndex)
    ###########################################################################
    # Create the latency and throughput dictionary with keys from the filters
    # We also want to store the throughput and packet loss related information
    # in there.
    ###########################################################################
    dict_lat = dict.fromkeys(filters.keys(), {})
    dict_tput = dict.fromkeys(filters.keys(), {})
    dict_tput["nicTput"] = throughput
    for tenant in filters.keys():
        #######################################################################
        # Need to reset endIndex to tput value to avoid zero value.
        # dict_tx/dict_rx are dictionaries of the per-tenant latencies.
        #######################################################################
        endIndex = tenantTput * (time - endOffset)
        dict_tx = {}
        dict_rx = {}
        dict_tput[tenant]["tenantTput"] = tenantTput
        #######################################################################
        # Print the timestamped packets for the tx and rx to stdout and then
        # proceed to process
        # ts = timestamp (float value)
        # token = packet count (integer, starts from 0)
        # token is used as the key for each packet in dict_tx/dict_rx
        # and ts is the value for the respective token
        #######################################################################
        stdout=RunCommand(ssh,"cd " + pcapAnalysisPath + "; cat " + pcapFiles[0] + "-"+ tenant)
        counter = 0
        for line in stdout:
            data = line.strip().split()
            ts = np.float(data[0])
            token = counter
            dict_tx[token] = ts
            counter += 1
        stdout=RunCommand(ssh,"cd " + pcapAnalysisPath + "; cat " + pcapFiles[1] + "-" + tenant)
        counter = 0
        for line in stdout:
            data = line.strip().split()
            ts = np.float(data[0])
            token = counter
            dict_rx[token] = ts
            counter += 1
        #######################################################################
        # limit is the total number of packets forwarded
        # We then check
        # * if we got more than we received (duplicates)
        # * if we received the same number of packets as sent
        # * if we got less than what we sent, packet loss!
        # If we get packet loss, calculate how many packets are missing and
        # shift the startIndex by the difference and then set packetLoss
        # to True.
        # If endIndex is more than the limit, we definitely lost packets
        # @10kpps we didn't see packet loss, however @40kpps there can be packet
        # loss. We are still investigating this issue.
        #######################################################################
        limit = len(dict_rx.keys())
        if len(dict_tx.keys()) < len(dict_rx.keys()):
            limit = len(dict_rx.keys())
            print "len(tx) < len(rx)."
        elif len(dict_tx.keys()) == len(dict_rx.keys()):
            print "len(tx) == len(rx)."
            dict_lat["limit"] = len(dict_rx.keys())
            dict_tput[tenant]["packetLoss"] = "False"
        else:
            print "len(tx) > len(rx), packet loss."
            print "need to set start index accordingly as there could be packet loss"
            rxLen = len(dict_rx.keys())
            txLen = len(dict_tx.keys())
            diff = txLen - rxLen
            print "got diff: " + str(diff)
            startIndex = tenantTput*startOffset + diff
            print "changed startIndex to:" + str(startIndex)
            dict_lat["limit"] = limit
            dict_tput[tenant]["packetLoss"] = "True"
        if endIndex > limit:
            print "endIndex > dict_lat[limit], fewer packets than expected."
            endIndex = limit
            dict_tput[tenant]["packetLoss"] = "True"
        #######################################################################
        # If latency is in the order of milliseconds we want to be notified
        # as that's a long time.
        # Now compute the latency by simply subtracting the packets with the
        # same counter/key in the dict_rx and dict_tx and store that in the
        # dict_lat based on the tenant. It will be merged later.
        # Dump the per tenant latency dict to a json file for future reference
        # and scp it to the storage server
        #######################################################################
        millisecondLat = False
        for k in range(startIndex, endIndex):
            latency=float(dict_rx[k] - dict_tx[k])
            if latency * 1000 > 1:
                millisecondLat = True
            dict_lat[tenant][k] = latency
        if millisecondLat is True:
           print "got latency > 1 ms for this tenant"
        with open('/tmp/' + topology + '-latency-' + vswitchMode + '-' + pktSize + '-'+tenant+'.res', 'w') as f:
            json.dump(dict_lat[tenant], f, indent=4)
            f.write("\n")
        scpLocalToRemote(cnx_spree, cnx, sourcePath='/tmp/',
                         sourceFiles=[topology + '-latency-' + vswitchMode + '-' + pktSize + '-'+tenant+'.res'],
                         destPath=pcapAnalysisPath)
    ###########################################################################
    # Now to merge the per-tenant latencies into one dictionary, then dump
    # that into a json and then scp them to the storage server.
    ###########################################################################
    dict_lat_merged = {}
    i = 0
    for tenant in dict_lat.keys():
        if tenant == "limit":
            continue
        tenant_dict = dict_lat[tenant]
        for j in tenant_dict.keys():
            dict_lat_merged[i] = tenant_dict[j]
            i += 1
    f = open('/tmp/' + topology + '-latency-' + vswitchMode + '-' + pktSize + '.res', 'w')
    f.write(json.dumps(dict_lat_merged) + '\n')
    f.close()
    scpLocalToRemote(cnx_spree, cnx, sourcePath='/tmp/', sourceFiles=[topology + '-latency-' + vswitchMode + '-' + pktSize + '.res'],
                     destPath=pcapAnalysisPath)
    f = open('/tmp/' + topology + '-latency-' + vswitchMode + '-' + pktSize + '-tput.res', 'w')
    f.write(json.dumps(dict_tput))
    f.close()
    scpLocalToRemote(cnx_spree, cnx, sourcePath='/tmp/', sourceFiles=[topology + '-latency-' + vswitchMode + '-' + pktSize + '-tput.res'],
                     destPath=pcapAnalysisPath)
    ssh.close()
    return dict_lat

'''
scp files recursively from one server to another
@src_cnx the source server
@dst_cnx the destination server
@sourcePath the path to the files on the source server
@sourceFiles the list of source files
@destPath the path on the destination server
'''
def scp(src_cnx, dst_cnx, sourcePath, sourceFiles, destPath):
    print "scp()"
    ssh=SSHConnect(dst_cnx)
    RunCommand(ssh, "mkdir -p "+destPath)
    for f in sourceFiles:
        stdout=RunCommand(ssh, "scp -r root@"+src_cnx[1]+":"+sourcePath+f+" "+destPath)
    ssh.close()

'''
scp files from the local server to a remote server
@src_cnx the source server
@dst_cnx the destination server
@sourcePath the path to the files on the source server
@sourceFiles the list of source files
@destPath the path on the destination server
'''
def scpLocalToRemote(src_cnx, dst_cnx, sourcePath, sourceFiles, destPath):
    print "scpLocalToRemote()"
    ssh=SSHConnect(src_cnx)
    for f in sourceFiles:
        RunCommand(ssh, "scp "+sourcePath+f+" root@"+dst_cnx[1]+":"+destPath)
    ssh.close()
